"""PoC prerequisite sorting."""
from typing import List

# Define types.
Cid = int
CardGraph = dict[Cid, List[Cid]]


def main() -> None:
    """Run the program."""

    # Create example data.
    requirement_graph: CardGraph = {1: [2, 3],  # cid=1 with prerequisites 2 and 3
                                    2: [3],     # cid=2 with prerequisite 3
                                    3: [],      # cid=3 has no prerequisites
                                    4: [2]}     # cid=4 with prerequisite 2
    # TODO: We should be able to generate enablement_graph by inverting requirement_graph.
    enablement_graph: CardGraph = {1: [],      # cid=1 is not a prerequisites of any cards
                                   2: [1, 4],  # cid=2 is a prerequisite of 1
                                   3: [1, 2],  # cid=3 is a prerequisite of 1 and 2
                                   4: []}      # cid=2 is not a prerequisite of any cards

    card_queue: List[Cid] = []

    # TODO: Reorder requirement_graph based on the new card positions of each cid and reorder
    # TODO: the list values of each entry in enablement_graph by the same criteria.
    # def new_card_position(cid):
    #     return cid  # For now, simply use cid. Later, we will need to query the database.

    requirement_keys = list(requirement_graph.keys())

    def add_and_prune(cid, iteration_index):
        recursion_index = requirement_keys.index(cid)
        is_upcoming_cid = recursion_index > iteration_index

        # If cid still has unmet requirements,
        # then it is not ready to be added to the card_queue.
        if len(requirement_graph[cid]) > 0:
            return

        # If cid is at the current index (as occurs at each iteration step,
        # at the top of each recursion), or is a previous index
        # (meaning it was already passed in the iteration but still had unmet requirements),
        # then add it to the card_queue and set the list of requirements to None instead of an
        # empty list. Upcoming cards will be added to the card_queue at later step in the iteration.
        if not is_upcoming_cid:
            card_queue.append(cid)
            requirement_graph[cid] = None

            # When cid is added to the card_queue, it can enable a list of other cards,
            # which are stored in enablement_graph[cid].
            for enabled_cid in enablement_graph[cid]:
                # if cid in requirement_graph[enabled_cid]:
                requirement_graph[enabled_cid].remove(cid)
                add_and_prune(enabled_cid, iteration_index)

    print(requirement_graph)
    print(card_queue)

    for index, key in enumerate(requirement_graph.keys()):
        add_and_prune(key, index)

    print(requirement_graph)
    print(card_queue)


if __name__ == '__main__':
    main()