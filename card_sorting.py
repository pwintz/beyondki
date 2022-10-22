"""PoC prerequisite sorting."""

import beyondki.sorting


def main() -> None:
    """Run the program."""

    import sys
    sys.setrecursionlimit(1000)
    n_cards = 2500 # Works OK up to 1500 with 'dense_prereqs' and up to >1200 with 'sparse_prereqs'.
    cid = list(range(1, n_cards))

    def dense_prereqs(cid):
        # Create a maximally dense requirement_graph by making each card depend on all other
        # cards that have a lower cid.
        return list(range(1, cid))

    def sparse_prereqs(cid):
        # Create a sparse prerequisite graph.
        if cid <= 60:
            return []
        return [cid-59, cid-60]

    def reverse_cid_order(cid):
        return -cid

    sorter = beyondki.sorting.CardSorter(cid, sparse_prereqs, reverse_cid_order)
    card_queue = sorter.sort()

    print(card_queue)


if __name__ == '__main__':
    main()