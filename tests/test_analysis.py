from datetime import datetime, timedelta, timezone

from batter.analysis import Event, leave_one_session_out


def make_session(individual, session, cell, zbin, n=80, offset=0):
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=offset)
    return [
        Event(individual, t0 + timedelta(seconds=30*i), cell, zbin, session)
        for i in range(n)
    ]


def test_repeatable_individuality_beats_population():
    events = []
    events += make_session("A", "A::S1", (1, 1), 1, offset=0)
    events += make_session("A", "A::S2", (1, 1), 1, offset=1)
    events += make_session("B", "B::S1", (1, 1), 6, offset=0)
    events += make_session("B", "B::S2", (1, 1), 6, offset=1)
    result = leave_one_session_out(events, minimum_scored_fixes=50)
    assert result["eligible_individual_count"] == 2
    assert result["equal_individual_mean_gain_nats_per_fix"] > 0
    assert result["positive_individual_fraction"] == 1.0


def test_location_by_identity_is_separate_from_marginal_altitude_identity():
    events = []
    # Both bats have the same 50/50 marginal altitude distribution, but each
    # repeats an opposite cell-specific vertical rule across sessions.
    for individual, mapping in {
        "A": [((1, 1), 1), ((2, 2), 6)],
        "B": [((1, 1), 6), ((2, 2), 1)],
    }.items():
        for session_no in (1, 2):
            session = f"{individual}::S{session_no}"
            for cell, zbin in mapping:
                events += make_session(
                    individual, session, cell, zbin, n=60,
                    offset=session_no - 1,
                )
    result = leave_one_session_out(events, minimum_scored_fixes=50)
    d = result["decomposition"]
    assert result["equal_individual_mean_gain_nats_per_fix"] > 0
    assert abs(d["equal_individual_mean_marginal_identity_gain_nats_per_fix"]) < 0.05
    assert d["equal_individual_mean_identity_x_location_gain_nats_per_fix"] > 0
