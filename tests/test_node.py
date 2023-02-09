from pickle import load


def test_detect_switch():
    topology = load(open("tests/topologies/switch.pickle", "rb"))

    switch_count = 0

    for node in topology.nodes.values():
        if node.is_switch():
            switch_count += 1

    assert switch_count == 1


def test_dont_detect_straight():
    topology = load(open("tests/topologies/straight_track.pickle", "rb"))

    switch_count = 0

    for node in topology.nodes.values():
        if node.is_switch():
            switch_count += 1

    assert switch_count == 0
