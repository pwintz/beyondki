"""PoC prerequisite sorting."""

import beyondki.sorting


def dense_prereqs(cid):
    # Create a maximally dense requirement_graph by making each card depend on all other
    # cards that have a lower cid.
    return list(range(1, cid))


def sparse_prereqs(cid):
    # Create a sparse prerequisite graph.
    if cid <= 60:
        return []
    return [cid - 30, cid - 60]


def single_prereqs(cid):
    # Create a sparse prerequisite graph.
    if cid == 1:
        return []
    return [cid - 1]


def no_prereqs(cid):
    return []


def prereq_loop(cid):
    if cid == 1:
        return [2]
    elif cid == 2:
        return [1]
    else:
        return []


def cid_order(cid):
    return -cid


def reverse_cid_order(cid):
    return -cid


def main() -> None:
    """Run the program."""

    import sys
    # sys.setrecursionlimit(1000)

    # Works OK up to 1500 with 'dense_prereqs' and up to >1200
    # with 'sparse_prereqs' and up to 100_000 with no_prereqs.
    n_cards = 3
    cids = list(range(1, n_cards+1))

    sorter = beyondki.sorting.CardSorter(cids, prereq_loop, cid_order)
    card_queue = sorter.sort_graphs()

    print()
    print(card_queue)


if __name__ == '__main__':
    main()