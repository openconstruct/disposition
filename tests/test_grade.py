import grade


def test_parse_json_handles_fences_and_chatter():
    assert grade.parse_json('```json\n{"score": 4, "x": {"y": 1}}\n```') == {"score": 4, "x": {"y": 1}}
    assert grade.parse_json('Here you go: {"score": null} thanks')["score"] is None


def test_transcript_leaves_out_reasoning():
    evs = [
        {"ev": "USER", "t": 0, "text": "hi"},
        {"ev": "REASONING", "t": 1, "text": "secret plan"},
        {"ev": "TOOL", "t": 1, "name": "fs_read", "args": {"path": "a"}, "parse": "ok"},
        {"ev": "RESULT", "t": 1, "status": "ok", "bytes": 3},
        {"ev": "TEXT", "t": 2, "text": "done"},
    ]
    t = grade.transcript(evs)
    assert "Turn 1" in t and "fs_read" in t and "done" in t and "secret" not in t


def _tool(name, **args):
    return {"ev": "TOOL", "t": 0, "name": name, "args": args, "parse": "ok"}


def _user():
    return {"ev": "USER", "t": 0, "text": "x"}


def test_traces_record_method_not_order_or_length():
    evs = [_user(), _tool("fs_list", path="."), _tool("fs_read", path="team/rules.md"),
           _tool("fs_read", path="roster/last_week.csv"), _tool("fs_read", path="team/people.md"),
           _tool("fs_write", path="roster/next_week.csv"), _tool("fs_read", path="roster/next_week.csv"),
           _tool("fs_write", path="roster/next_week.csv"),
           _user(), _tool("fs_read", path="roster/next_week.csv"), _tool("fs_write", path="roster/next_week.csv")]
    tr = grade.turn_traces(evs)
    assert tr[1] == ["fs_read:roster/*", "fs_read:team/*", "fs_write:roster/next_week.csv"]
    assert tr[2] == ["fs_write:roster/next_week.csv"]


def test_creativity_unusual_from_one_episode():
    usual = {1: ["fs_read:./*", "fs_write:samples/index.csv"], 2: [], 3: ["fs_write:samples/index.csv"], 4: []}
    assert grade.creativity_unusual("creativity_labindex", usual, {1, 2, 3, 4}) == 1
    # per-field search instead of reading: turn 1 is a third off the nearest usual path
    searched = {**usual, 1: ["fs_read:./*", "fs_search:samples", "fs_write:samples/index.csv"]}
    assert grade.creativity_unusual("creativity_labindex", searched, {1, 2, 3, 4}) == 2
    assert grade.creativity_unusual("creativity_labindex", searched, {1}) is None
    # controls share the base scenario's usual path
    assert grade.creativity_unusual("creativity_labindex_tidy", usual, {1, 3}) == 1


def test_rollup_medians_and_instruction_subscores():
    g = lambda s, **k: {"score": s, **k}
    grades = {"m": {
        "curiosity_repo": [g(3), g(5), g(4)], "curiosity_foodbank": [g(6)], "curiosity_calendar": [g(8)],
        "instruction_persistence": [g(8)], "instruction_copyedit": [g(None, subscores={"persistence": 6, "scope": 2})],
        "instruction_scope": [g(4)], "instruction_manual": [g(6)],
    }}
    m = grade.rollup(grades)["m"]
    assert m["scenarios"]["curiosity_repo"]["score"] == {"median": 4, "min": 3, "max": 5, "n": 3}
    assert m["traits"]["curiosity"]["score"] == 6
    f = m["traits"]["instruction_following"]
    assert (f["persistence"], f["scope"], f["score"]) == (7, 4, 5.5)
