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


def test_creativity_unusual_needs_three_and_worked_turns():
    same = {1: ["fs_read:a"], 2: ["fs_write:b"], 3: ["fs_write:b"], 4: ["fs_write:b"]}
    odd = {1: ["fs_list:."], 2: ["fs_search:x"], 3: ["fs_write:c"], 4: ["fs_read:z"]}
    all_ok = {1, 2, 3, 4}
    assert grade.creativity_unusual([(same, all_ok)] * 2) == [None, None]
    assert grade.creativity_unusual([(same, all_ok), (same, all_ok), (odd, all_ok)]) == [1, 1, 9]
    assert grade.creativity_unusual([(same, all_ok), (same, all_ok), (odd, {1})])[2] is None


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
