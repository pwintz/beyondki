"""Unit tests for ``sorting`` module."""
from typing import List

import pytest
from beartype import beartype

from beyondki.sorting import generate_card_graphs, PrerequisiteLoopError, Cid, CardGraph, sort_graphs


def cid_order(cid: Cid) -> int:
    return cid


def reverse_cid_order(cid: Cid) -> int:
    return -cid


# noinspection PyUnusedLocal
def no_prereqs(cid: Cid) -> list[Cid]:
    return []


def prereqs_fnc_from_dict(prereq_dict: dict[Cid, list[Cid]]):
    return lambda cid: prereq_dict[cid]


@beartype
def assert_equal_with_order(dict1: CardGraph,
                            dict2: CardGraph) -> None:
    assert dict1 == dict2                            # Check contents
    assert list(dict1.keys()) == list(dict2.keys())  # Check order


def test_single_card():
    cids = [1]
    requirement_graph, dependents_graph = generate_card_graphs(cids, no_prereqs, cid_order)
    assert requirement_graph == {1: []}
    assert dependents_graph == {1: []}


def test_nonexistent_prereq():
    cids = [1]

    prereqs = prereqs_fnc_from_dict({1: [2]})

    with pytest.raises(ValueError):
        generate_card_graphs(cids, prereqs, cid_order)


def test_sorted_by_cid_wo_prereqs():
    cids = [2, 1]
    requirement_graph, dependents_graph = generate_card_graphs(cids, no_prereqs, cid_order)
    assert_equal_with_order(requirement_graph, {1: [], 2: []})
    assert_equal_with_order(dependents_graph, {1: [], 2: []})


def test_sorted_by_reverse_cid_wo_prereqs():
    cids = [1, 2]
    requirement_graph, dependents_graph = generate_card_graphs(cids, no_prereqs, reverse_cid_order)
    assert_equal_with_order(requirement_graph, {2: [], 1: []})
    assert_equal_with_order(dependents_graph, {2: [], 1: []})


def test_one_prereq():
    cids = [1, 2]

    def prereqs(cid):
        if cid == 1:
            return [2]
        elif cid == 2:
            return []

    requirement_graph, dependents_graph = generate_card_graphs(cids, prereqs, reverse_cid_order)
    assert_equal_with_order(requirement_graph, {2: [], 1: [2]})
    assert_equal_with_order(dependents_graph, {2: [1], 1: []})


def test_prereq_loop_raises_error():
    cids = [1, 2]

    def prereq_loop(cid):
        if cid == 1:
            return [2]
        elif cid == 2:
            return [1]

    requirement_graph, dependents_graph = generate_card_graphs(cids, prereq_loop, cid_order)
    with pytest.raises(PrerequisiteLoopError):
        sort_graphs(requirement_graph, dependents_graph)


def test_dependent_graph_values_are_sorted():
    cids = [2, 3, 1]

    def prereqs(cid):
        if cid == 1:
            return []
        else:
            return [1]

    requirement_graph, dependents_graph = generate_card_graphs(cids, prereqs, reverse_cid_order)
    assert_equal_with_order(requirement_graph, {3: [1], 2: [1], 1: []})
    assert_equal_with_order(dependents_graph, {3: [], 2: [], 1: [3, 2]})


def test_error_if_prereqs_not_a_list():
    # noinspection PyUnusedLocal
    def return_not_a_list(cid):
        return 1

    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        generate_card_graphs([1, 2], return_not_a_list, cid_order)
