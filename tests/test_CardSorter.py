"""Unit tests for ``sorting`` module."""
from typing import List

import pytest
from beartype import beartype

from beyondki.sorting import CardSorter, PrerequisiteLoopError


def cid_order(cid):
    return cid


def reverse_cid_order(cid):
    return -cid


# noinspection PyUnusedLocal
def no_prereqs(cid):
    return []


def prereqs_fnc_from_dict(prereq_dict):
    return lambda cid: prereq_dict[cid]


@beartype
def assert_equal_with_order(dict1: dict[int, List[int]],
                            dict2: dict[int, List[int]]) -> None:
    assert dict1 == dict2                            # Check contents
    assert list(dict1.keys()) == list(dict2.keys())  # Check order


def test_single_card():
    cids = [1]
    card_sorter = CardSorter(cids, no_prereqs, cid_order)
    assert card_sorter.cids == [1]
    assert card_sorter.requirement_graph == {1: []}
    assert card_sorter.dependents_graph == {1: []}


def test_nonexistent_prereq():
    cids = [1]

    prereqs = prereqs_fnc_from_dict({1: [2]})

    with pytest.raises(ValueError):
        CardSorter(cids, prereqs, cid_order)


def test_sorted_by_cid_wo_prereqs():
    cids = [2, 1]
    card_sorter = CardSorter(cids, no_prereqs, cid_order)
    assert card_sorter.cids == [1, 2]
    assert_equal_with_order(card_sorter.requirement_graph, {1: [], 2: []})
    assert_equal_with_order(card_sorter.dependents_graph, {1: [], 2: []})


def test_sorted_by_reverse_cid_wo_prereqs():
    cids = [1, 2]
    card_sorter = CardSorter(cids, no_prereqs, reverse_cid_order)
    assert card_sorter.cids == [2, 1]
    assert_equal_with_order(card_sorter.requirement_graph, {2: [], 1: []})
    assert_equal_with_order(card_sorter.dependents_graph, {2: [], 1: []})


def test_one_prereq():
    cids = [1, 2]

    def prereqs(cid):
        if cid == 1:
            return [2]
        elif cid == 2:
            return []

    card_sorter = CardSorter(cids, prereqs, reverse_cid_order)
    assert_equal_with_order(card_sorter.requirement_graph, {2: [], 1: [2]})
    assert_equal_with_order(card_sorter.dependents_graph, {2: [1], 1: []})


def test_prereq_loop_raises_error():
    cids = [1, 2]

    def prereq_loop(cid):
        if cid == 1:
            return [2]
        elif cid == 2:
            return [1]

    sorter = CardSorter(cids, prereq_loop, cid_order)
    with pytest.raises(PrerequisiteLoopError):
        sorter.sort()


def test_dependent_graph_values_are_sorted():
    cids = [2, 3, 1]

    def prereqs(cid):
        if cid == 1:
            return []
        else:
            return [1]

    card_sorter = CardSorter(cids, prereqs, reverse_cid_order)
    assert_equal_with_order(card_sorter.requirement_graph, {3: [1], 2: [1], 1: []})
    assert_equal_with_order(card_sorter.dependents_graph, {3: [], 2: [], 1: [3, 2]})


def test_error_if_prereqs_not_a_list():
    # noinspection PyUnusedLocal
    def return_not_a_list(cid):
        return 1

    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        CardSorter([1, 2], return_not_a_list, cid_order)
