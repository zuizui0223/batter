#!/usr/bin/env python3
"""Additive, post-primary-inspection audit of deer personal CRPS weights.

The frozen 5-km primary cohorts, masks, profiles and personal model are retained.
An equal-animal anonymous pool uses exactly the same qualified training records
as each personal model, including the focal animal. Only aggregate results are
serialized. No identity test, population interval or biological p-value is made.
"""
from __future__ import annotations

import argparse
import calendar
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from deer_seasonal_rx_v1 import (
    WeightedDistribution, _fold_support, balanced_profile, distribution_summary,
    mean, outcome, peer_distribution, seasonal_individual_r, write_json,
)

TOLERANCE = 1e-11
GAIN_COMPONENTS = ('original_peer_gain', 'identity_weight_gain', 'data_addition_gain')


def audit_models(profiles, target, n_train_days, anonymous=None):
    """Preserve the personal model; add the all-animal, same-record comparator."""
    if target not in profiles or len(profiles) < 2 or n_train_days < 3:
        raise ValueError('Audit models require a qualified focal profile and peers')
    peer = peer_distribution(profiles, target)
    pool = anonymous if anonymous is not None else WeightedDistribution.mixture(
        [(profile, 1 / len(profiles)) for profile in profiles.values()])
    alpha = n_train_days / (n_train_days + 5)
    personal = WeightedDistribution.mixture(
        [(peer, 1 - alpha), (profiles[target], alpha)])
    return peer, pool, personal


def _decomposition_error(original, identity, addition):
    if original is None:
        if identity is not None or addition is not None:
            raise AssertionError('Missing gain components disagree')
        return 0.0
    error = abs(original - identity - addition)
    if error > TOLERANCE:
        raise AssertionError('Gain decomposition exceeds the fixed tolerance')
    return error


def analyze_month_audit(steps, year, month, lat_cos):
    """Reconstruct primary support before scoring, with no new eligibility rule."""
    rows = [r for r in steps if r.year == year and r.month == month]
    by_animal = defaultdict(list)
    for row in rows:
        by_animal[row.animal].append(row)
    initial = {a for a, seq in by_animal.items()
               if len(seq) >= 80 and len({r.day for r in seq}) >= 10}
    eligible = [r for r in rows if r.animal in initial]
    split = calendar.monthrange(year, month)[1] // 2
    first = [r for r in eligible if r.dt.day <= split]
    second = [r for r in eligible if r.dt.day > split]
    folds = [_fold_support(first, second, 5, lat_cos, (0, 0)),
             _fold_support(second, first, 5, lat_cos, (0, 0))]
    for fold in folds:
        if fold['train_dates'] & fold['test_dates']:
            raise AssertionError('Training and test dates overlap')
    animals = set(folds[0]['evaluated']) & set(folds[1]['evaluated'])
    report = {
        'year': year, 'month': month, 'context_km': 5,
        'origin_x_fraction': 0, 'origin_y_fraction': 0,
        'n_source_step_animals': len(by_animal), 'n_initial_animals': len(initial),
        'n_evaluated_animals': len(animals), 'all_source_month_steps': len(rows),
        'initial_eligible_steps': len(eligible), 'calendar_separation_verified': True,
        'fold_support': [
            {'n_qualified_training_animals': len({a for a, _ in fold['qualified']}),
             'n_common_contexts': len(fold['common']),
             'n_evaluation_eligible_animals': len(fold['evaluated'])} for fold in folds],
        'status': ('DESCRIPTIVE_SAME_RECORD_WEIGHT_AUDIT' if len(animals) >= 2 else
                   'NOT_ESTIMABLE_BOTH_FOLDS_COMMON_CONTEXT_SUPPORT'),
        'peer_CRPS': None, 'anonymous_pool_CRPS': None, 'personal_CRPS': None,
        **{name: None for name in GAIN_COMPONENTS},
        'heldout_steps': 0, 'heldout_animal_days': 0,
        'max_absolute_decomposition_error': 0.0,
    }
    internal = {'animals': animals, 'animal_gains': {name: {} for name in GAIN_COMPONENTS}}
    if len(animals) < 2:
        return report, internal

    daily_scores = defaultdict(lambda: defaultdict(list))
    peer_counts = []
    for fold in folds:
        profiles = defaultdict(dict)
        days = {}
        for (animal, ctx), seq in fold['qualified'].items():
            if ctx in fold['common']:
                profiles[ctx][animal] = balanced_profile((r.day, outcome(r)) for r in seq)
                days[(animal, ctx)] = len({r.day for r in seq})
        anonymous = {
            ctx: WeightedDistribution.mixture(
                [(profile, 1 / len(by_id)) for profile in by_id.values()])
            for ctx, by_id in profiles.items()}
        model_cache = {}
        for animal in sorted(animals):
            for row, ctx in fold['evaluated'][animal]:
                key = (animal, ctx)
                if key not in model_cache:
                    model_cache[key] = audit_models(
                        profiles[ctx], animal, days[key], anonymous[ctx])
                y = outcome(row)
                daily_scores[animal][row.day].append(
                    tuple(model.crps(y) for model in model_cache[key]))
                peer_counts.append(len(profiles[ctx]) - 1)

    animal_scores = {
        animal: tuple(mean(mean(score[index] for score in seq) for seq in daily.values())
                      for index in range(3))
        for animal, daily in daily_scores.items()}
    gains = internal['animal_gains']
    errors = []
    for animal in sorted(animals):
        peer, pool, personal = animal_scores[animal]
        gains['original_peer_gain'][animal] = peer - personal
        gains['identity_weight_gain'][animal] = pool - personal
        gains['data_addition_gain'][animal] = peer - pool
        errors.append(_decomposition_error(*(gains[key][animal] for key in GAIN_COMPONENTS)))
    cohort_scores = [mean(scores[index] for scores in animal_scores.values())
                     for index in range(3)]
    report.update(dict(zip(('peer_CRPS', 'anonymous_pool_CRPS', 'personal_CRPS'), cohort_scores)))
    report.update({key: mean(gains[key].values()) for key in GAIN_COMPONENTS})
    errors.append(_decomposition_error(*(report[key] for key in GAIN_COMPONENTS)))
    report.update({
        'heldout_steps': sum(len(seq) for daily in daily_scores.values() for seq in daily.values()),
        'heldout_animal_days': sum(len(daily) for daily in daily_scores.values()),
        'all_steps_from_final_animals': sum(len(by_animal[a]) for a in animals),
        'other_training_animals_per_scored_step': distribution_summary(peer_counts),
        'individual_gain_distributions': {
            key: distribution_summary(gains[key].values()) for key in GAIN_COMPONENTS},
        'fraction_animals_positive_gain': {
            key: sum(v > 0 for v in gains[key].values()) / len(animals) for key in GAIN_COMPONENTS},
        'max_absolute_decomposition_error': max(errors),
    })
    report['heldout_step_fraction_final_animals'] = (
        report['heldout_steps'] / report['all_steps_from_final_animals'])
    return report, internal


def reconcile_primary(audit, primary):
    """Refuse output if any fixed cohort/support aggregate or primary score moves."""
    fields = ('year', 'month', 'context_km', 'origin_x_fraction', 'origin_y_fraction',
              'n_source_step_animals', 'n_initial_animals', 'n_evaluated_animals',
              'all_source_month_steps', 'initial_eligible_steps',
              'calendar_separation_verified', 'fold_support',
              'heldout_steps', 'heldout_animal_days')
    for key in fields:
        if audit[key] != primary[key]:
            raise AssertionError('Audit changed primary support field: ' + key)
    for key in ('all_steps_from_final_animals', 'heldout_step_fraction_final_animals',
                'other_training_animals_per_scored_step'):
        if audit.get(key) != primary.get(key):
            raise AssertionError('Audit changed primary denominator field: ' + key)
    differences = []
    for audit_key, primary_key in [('original_peer_gain', 'R_gain'),
                                   ('peer_CRPS', 'peer_CRPS'),
                                   ('personal_CRPS', 'personal_CRPS')]:
        a, p = audit[audit_key], primary[primary_key]
        if a is None or p is None:
            if a is not None or p is not None:
                raise AssertionError('Primary and audit score availability disagree')
        else:
            difference = abs(a - p)
            if difference > TOLERANCE:
                raise AssertionError('Audit changed primary score: ' + primary_key)
            differences.append(difference)
    return {'support_aggregates_identical': True,
            'max_absolute_score_difference': max(differences, default=0.0),
            'absolute_tolerance': TOLERANCE}


def seasonal_audit(monthly_components):
    """Use the same >=2-month/season paired-animal rule for every component."""
    availability = [
        {month: set(gains) for month, gains in monthly_components[key].items()}
        for key in GAIN_COMPONENTS]
    if any(value != availability[0] for value in availability[1:]):
        raise AssertionError('Seasonal gain components have different animal masks')
    result = {}
    for key in GAIN_COMPONENTS:
        contrast = seasonal_individual_r(monthly_components[key])
        result[key] = {
            'n_matched_animals': contrast['n_matched_animals'],
            'winter_mean_gain': contrast['winter_mean_R'],
            'summer_mean_gain': contrast['summer_mean_R'],
            'winter_minus_summer_gain': contrast['winter_minus_summer_R'],
            'individual_difference_distribution': contrast['individual_difference_distribution'],
            'peer_reference_changes_across_months': True,
        }
    errors = [_decomposition_error(*(result[key][field] for key in GAIN_COMPONENTS))
              for field in ('winter_mean_gain', 'summer_mean_gain', 'winter_minus_summer_gain')]
    result['max_absolute_decomposition_error'] = max(errors)
    return result


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconcile_source_audits(event_audit, step_audit, primary):
    # JSON saves integer year keys as strings. Compare the serialized data model
    # used by the frozen result, without dropping or rounding any count or field.
    current = json.loads(json.dumps({'event_audit': event_audit, 'step_audit': step_audit},
                                    allow_nan=False))
    if any(current[key] != primary[key] for key in current):
        raise AssertionError('Source event or step audit differs from the primary result')


def run(events_path, reference_path, primary_path, output):
    from deer_source_pipeline_v1 import load_source, make_steps, source_lat_cos, group_steps_by_month
    root = Path(__file__).resolve().parent
    primary = json.loads(primary_path.read_text())
    script_names = ('deer_source_pipeline_v1.py', 'deer_seasonal_rx_v1.py',
                    'deer_equal_data_audit_v1.py')
    script_hashes = {name: _sha256(root / name) for name in script_names}
    for name in script_names[:2]:
        if script_hashes[name] != primary['script_sha256'][name]:
            raise AssertionError('Frozen source or primary scoring script changed')
    expected_months = {(year, month) for year in (2018, 2019, 2020) for month in range(1, 13)}
    primary_months = {(r['year'], r['month']): r for r in primary['monthly']}
    if set(primary_months) != expected_months or len(primary['monthly']) != 36:
        raise AssertionError('Primary result must contain exactly the frozen 36 months')
    events, event_audit, receipts = load_source(events_path, reference_path)
    steps, step_audit = make_steps(events)
    if receipts != primary['source_receipts']:
        raise AssertionError('Source receipts differ from the primary result')
    reconcile_source_audits(event_audit, step_audit, primary)
    lat_cos = source_lat_cos(events)
    by_steps = group_steps_by_month(steps)
    result = {
        'schema_version': 1, 'as_of': '2026-10-20',
        'audit_stage': 'POST_PRIMARY_PEER_GAIN_INSPECTION',
        'timing_disclosure': 'Added after initial 2018 primary peer-gain outcomes were inspected; not part of the original frozen design',
        'scope': 'All 36 original primary 5-km, origin-zero months; no new filters, thresholds, cohort selection or sensitivity selection',
        'source_doi': primary['source_doi'], 'source_receipts': receipts,
        'primary_result_sha256': _sha256(primary_path),
        'original_design_sha256': primary['design_sha256'],
        'script_sha256': script_hashes,
        'test_script_sha256': _sha256(root / 'tests' / 'test_deer_equal_data_audit_v1.py'),
        'source_clock_verified_UTC': False,
        'outcome': 'log1p(2h-standardized endpoint displacement/0.1 km)',
        'anonymous_pool': 'Equal weight to every qualified training animal in the context, including the focal animal; equal observed dates then steps within each animal',
        'personal_model': 'Unchanged: focal empirical profile weight d/(d+5), peer-only pool weight 5/(d+5), with d distinct focal training dates in the context',
        'evaluation_weighting': 'Unchanged fixed heldout steps, equal test dates within animal, then equal final animals across both calendar folds',
        'gain_definitions': {
            'original_peer_gain': 'peer_CRPS - personal_CRPS',
            'identity_weight_gain': 'anonymous_pool_CRPS - personal_CRPS',
            'data_addition_gain': 'peer_CRPS - anonymous_pool_CRPS',
        },
        'interpretation': {
            'original_peer_gain': 'Can include gains from adding independent focal training data without persistent identity differences',
            'identity_weight_gain': 'Descriptive benefit of the frozen personal weights versus equal-animal weights on the same training records; not a calibrated biological identity effect',
            'data_addition_gain': 'Algebraic comparator contrast, not an isolated causal effect of sample size: focal mass changes and peer mass is diluted',
            'remaining_nuisance': 'Unequal training precision, observation quality and unmeasured context can affect the same-record contrast; within-source dependence and changing peer reference remain',
        },
        'uncertainty': 'Empirical animal distributions and paired seasonal descriptions only; no population confidence intervals or biological p-values',
        'monthly': [], 'seasonal_paired_gain': [],
    }
    yearly = {year: {key: {} for key in GAIN_COMPONENTS} for year in (2018, 2019, 2020)}
    for year, month in sorted(expected_months):
        report, internal = analyze_month_audit(by_steps.get((year, month), []), year, month, lat_cos)
        report['primary_reconciliation'] = reconcile_primary(report, primary_months[(year, month)])
        result['monthly'].append(report)
        for key in GAIN_COMPONENTS:
            yearly[year][key][month] = internal['animal_gains'][key]
        print(json.dumps({'year': year, 'month': month,
                          'n_evaluated_animals': report['n_evaluated_animals'],
                          'primary_reconciled': True}), flush=True)
    for year in (2018, 2019, 2020):
        contrast = seasonal_audit(yearly[year])
        contrast['year'] = year
        result['seasonal_paired_gain'].append(contrast)
    result['reconciliation'] = {
        'months_verified': len(result['monthly']),
        'source_receipts_identical': True, 'event_and_step_audits_identical': True,
        'support_aggregates_identical': True, 'absolute_tolerance': TOLERANCE,
        'max_absolute_primary_score_difference': max(
            r['primary_reconciliation']['max_absolute_score_difference'] for r in result['monthly']),
        'max_absolute_gain_decomposition_error': max(
            r['max_absolute_decomposition_error']
            for r in result['monthly'] + result['seasonal_paired_gain']),
    }
    write_json(output, result)
    print(json.dumps({'output': str(output), 'n_months': len(result['monthly']),
                      'reconciliation': result['reconciliation']}), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--events', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--primary-result', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.events, args.reference, args.primary_result, args.output)


if __name__ == '__main__':
    main()
