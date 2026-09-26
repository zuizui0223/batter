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
