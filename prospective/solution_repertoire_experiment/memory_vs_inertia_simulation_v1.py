from __future__ import annotations
import argparse
import itertools
import json
import math
from pathlib import Path
import numpy as np
N_ANIMALS = 20
N_BLOCKS = 5
N_REPLICATES = 1000
N_ROUTES = 4
PROBE_LEN = 16
HALF = 8
FORCED_R1_LEN = 8
POST_LEN = 8
ALPHA = 0.5
S2_N_PERM = 999
ROOT_SEED = 202610081337
SCENARIOS = (('IID_NULL', 'inertia', 0.0, 0.0), ('PERSISTENT_STRONG', 'stable', 4.0, 40.0), ('PERSISTENT_MODERATE', 'stable', 8.0, 30.0), ('INERTIA_MODERATE', 'inertia', 0.8, 0.1), ('INERTIA_STRONG', 'inertia', 0.95, 0.1), ('INERTIA_EQUAL', 'inertia', 0.95, 0.95))

def legal_assignments():
    local = ((1, -1, 1, -1), (1, -1, -1, 1), (-1, 1, 1, -1), (-1, 1, -1, 1))
    signs = np.asarray([sum((tuple(choice) for choice in comb), ()) for comb in itertools.product(local, repeat=N_BLOCKS)], dtype=np.int8)
    return signs

def score_routes(probe: np.ndarray) -> np.ndarray:
    n, t = probe.shape
    assert t == 16 and n >= 4
    counts = np.zeros((n, N_ROUTES), dtype=np.int64)
    np.add.at(counts, (np.repeat(np.arange(n), HALF), probe[:, :HALF].reshape(-1)), 1)
    logp = np.log((counts + ALPHA) / (HALF + ALPHA * N_ROUTES))
    other_logp = (logp.sum(axis=0, keepdims=True) - logp) / (n - 1)
    margin = logp - other_logp
    return margin[np.arange(n)[:, None], probe[:, HALF:]].mean(axis=1)

def slow_reference_R(probe):
    n = len(probe)
    routeprob = []
    for i in range(n):
        prob = [(sum((int(x == r) for x in probe[i, :8])) + 0.5) / 10.0 for r in range(4)]
        routeprob.append(prob)
    out = []
    for i in range(n):
        v = []
        for r in probe[i, 8:]:
            own = math.log(routeprob[i][r])
            others = sum((math.log(routeprob[j][r]) for j in range(n) if j != i)) / (n - 1)
            v.append(own - others)
        out.append(sum(v) / len(v))
    return np.array(out)

def generate_family(rng, opened, mode, first_parameter, second_parameter):
    n = len(opened)
    parameter = np.where(opened, first_parameter, second_parameter)
    if mode == 'stable':
        gamma = np.stack([rng.gamma(k / 4, 1.0, size=4) for k in parameter])
        theta = gamma / gamma.sum(axis=1, keepdims=True)
        cumulative = theta.cumsum(axis=1)
        def draw(length):
            uniform = rng.random((n, length))
            return np.sum(uniform[:, :, None] > cumulative[:, None, :], axis=2).astype(np.int8)
        return (draw(PROBE_LEN), draw(POST_LEN))
    assert mode == 'inertia'
    routes = np.empty((n, PROBE_LEN), dtype=np.int8)
    routes[:, 0] = rng.integers(0, N_ROUTES, size=n)
    for t in range(1, PROBE_LEN):
        reuse = rng.random(n) < parameter
        innovations = rng.integers(0, N_ROUTES, size=n)
        routes[:, t] = np.where(reuse, routes[:, t - 1], innovations)
    state = np.zeros(n, dtype=np.int8)
    post = np.empty((n, POST_LEN), dtype=np.int8)
    for t in range(POST_LEN):
        reuse = rng.random(n) < parameter
        innovations = rng.integers(0, N_ROUTES, size=n)
        state = np.where(reuse, state, innovations)
        post[:, t] = state
    return (routes, post)

def post_score_and_null(rng, initial_probe, post, eligible_idx):
    early = initial_probe[eligible_idx, :HALF]
    new = post[eligible_idx, :POST_LEN]
    m = len(eligible_idx)
    if m != 10:
        raise AssertionError('suppression group must have 10 OPEN-acquired bats')
    counts = np.zeros((m, 4), int)
    np.add.at(counts, (np.repeat(np.arange(m), HALF), early.ravel()), 1)
    logp = np.log((counts + 0.5) / 10)
    qcounts = np.zeros((m, 4), float)
    np.add.at(qcounts, (np.repeat(np.arange(m), POST_LEN), new.ravel()), 1)
    q = qcounts / POST_LEN
    const = np.sum(q * logp.sum(axis=0)[None, :]) / m / (m - 1)
    obs = m / (m - 1) * np.einsum('ir,ir->', q, logp) / m - const
    perms = np.argsort(rng.random((S2_N_PERM, m)), axis=1)
    permuted = m / (m - 1) * np.einsum('ir,pir->p', q, logp[perms]) / m - const
    return (float(obs), permuted)

def simulation_one(rng, scenario, assignments):
    label, mode, po, pc = scenario
    ix = int(rng.integers(0, len(assignments)))
    observed_sign = assignments[ix]
    a_open = observed_sign == 1
    probes_A, post_A = generate_family(rng, a_open, mode, po, pc)
    probes_B, post_B = generate_family(rng, ~a_open, mode, po, pc)
    rA = score_routes(probes_A)
    rB = score_routes(probes_B)
    diffs = rA - rB
    obs = float(np.dot(observed_sign, diffs) / N_ANIMALS)
    null = assignments @ diffs / N_ANIMALS
    p = float(np.count_nonzero(null >= obs - 1e-12) / len(null))
    p1 = bool(obs > 0 and p <= 0.05)
    sA, null_A = post_score_and_null(rng, probes_A, post_A, np.flatnonzero(a_open))
    sB, null_B = post_score_and_null(rng, probes_B, post_B, np.flatnonzero(~a_open))
    sobs = (sA + sB) / 2
    snull = (null_A + null_B) / 2
    sp = float((1 + np.count_nonzero(snull >= sobs - 1e-12)) / (S2_N_PERM + 1))
    s2 = bool(sobs > 0 and sp <= 0.05)
    return dict(P1_Delta=obs, P1_p=p, P1_positive=p1, S2_adv=sobs, S2_p=sp, S2_positive=s2)

def preflight():
    A = legal_assignments()
    assert A.shape == (1024, 20)
    assert len({tuple(r) for r in A}) == 1024
    for row in A:
        assert (row == 1).sum() == 10 and (row == -1).sum() == 10
        for k in range(5):
            b = row[4 * k:4 * k + 4]
            assert sorted(b[:2]) == [-1, 1] and sorted(b[2:]) == [-1, 1]
    synthetic = np.asarray([[(i * 3 + t * t + i * t // 3) % 4 for t in range(16)] for i in range(20)], dtype=np.int8)
    fast = score_routes(synthetic)
    slow = slow_reference_R(synthetic)
    assert np.allclose(fast, slow, rtol=0, atol=1e-13)
    assert np.all(np.isfinite(fast))
    all_r1 = np.zeros((20, 16), dtype=np.int8)
    assert np.allclose(score_routes(all_r1), 0, atol=1e-12)
    diff = np.linspace(-0.3, 0.5, 20)
    for observed in [0, 17, 101, 1023]:
        t = A[observed] @ diff / 20
        null = A @ diff / 20
        assert np.any(np.isclose(null, t, atol=1e-13))
    r1 = np.zeros(20, dtype=int)
    assert np.all(r1 == 0)
    return {'number_of_legal_assignments': len(A), 'test_primary_definition': 'PASS', 'test_stratum_balance': 'PASS', 'test_invariance_and_null_support': 'PASS'}

def mc_summary(rows, scenario):
    n = len(rows)
    q = lambda k: np.asarray([r[k] for r in rows])
    p = q('P1_positive').astype(bool)
    s = q('S2_positive').astype(bool)
    both = p & s
    def rate(a):
        v = float(np.mean(a))
        return {'count': int(np.sum(a)), 'frequency': v, 'mc_se': float(np.sqrt(v * (1 - v) / n))}
    return {'mechanism': scenario[1], 'parameters': {'open': scenario[2], 'constrained': scenario[3]}, 'n_synthetic_experiments': n, 'P1_mean_Delta': float(np.mean(q('P1_Delta'))), 'P1_median_Delta': float(np.median(q('P1_Delta'))), 'P1_rejection': rate(p), 'proposed_S2_mean_advantage': float(np.mean(q('S2_adv'))), 'proposed_S2_rejection': rate(s), 'both_P1_and_S2_rejection': rate(both), 'S2_given_P1_count': int(np.sum(both)), 'S2_given_P1_fraction': float(np.sum(both) / np.sum(p)) if np.any(p) else None, 'P1_p_median': float(np.median(q('P1_p'))), 'S2_p_median': float(np.median(q('S2_p'))}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--out', default='MEMORY_VS_INERTIA_SIMULATION_RESULT_V1.json')
    args = parser.parse_args()
    checks = preflight()
    if args.self_test:
        print(json.dumps(checks, indent=2))
        return
    ss = np.random.SeedSequence(ROOT_SEED)
    experiments = {}
    assignment = legal_assignments()
    for scenario, child in zip(SCENARIOS, ss.spawn(len(SCENARIOS))):
        v = [simulation_one(np.random.default_rng(rep_seed), scenario, assignment) for rep_seed in child.spawn(N_REPLICATES)]
        experiments[scenario[0]] = mc_summary(v, scenario)
        print(scenario[0], 'P1', experiments[scenario[0]]['P1_rejection'], 'S2', experiments[scenario[0]]['proposed_S2_rejection'], 'BOTH', experiments[scenario[0]]['both_P1_and_S2_rejection'], flush=True)
    out = {'status': 'SYNTHETIC_PLANNING_ONLY_NO_BAT_OUTCOMES', 'contract': 'MEMORY_VS_INERTIA_SIMULATION_CONTRACT_V1.md', 'source': 'fixed PR72 P1 design; hypothetical post-acquisition generative models', 'root_seed': ROOT_SEED, 'n_replicates_per_scenario': N_REPLICATES, 'n_legal_assignments': int(len(assignment)), 'n_s2_within_treatment_identity_permutations': S2_N_PERM, 'n_bats_per_experiment': N_ANIMALS, 'probe_flights_per_family': PROBE_LEN, 'forced_R1_trials_per_open_family': FORCED_R1_LEN, 'post_reopening_flights_per_open_family': POST_LEN, 'preflight': checks, 'experiments': experiments, 'limitations': ['P1 tests acquisition-treatment effects on predictive organization; it does not prove persistent preference.', 'Secondary 8 forced R1 + 8 reopened flights is a hypothetical numeric S2 planning variant and does not change PR72.', 'IID persistent theta and common Markov inertia are deliberately idealized alternatives; other mechanisms exist.', 'Simulated scenario rejection frequencies are not empirical bat effects or observed statistical power.']}
    Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True) + '\n', encoding='utf-8')
if __name__ == '__main__':
    main()
