from collections import Callable
from typing import Union

from beartype import beartype

# Define types.
# TODO: Move type definitions.
Cid = int
CardGraph = dict[Cid, Union[list[Cid], None]]


class CardSorter:
    cids: list[Cid]
    requirement_graph: CardGraph
    dependents_graph: CardGraph

    # Here are example data for the graphs:
    # requirement_graph = {1: [2, 3],  # cid=1 with prerequisites 2 and 3
    #                      2: [3],     # cid=2 with prerequisite 3
    #                      3: [],      # cid=3 has no prerequisites
    #                      4: [2]}     # cid=4 with prerequisite 2
    # dependents_graph = {1: [],      # cid=1 is not a prerequisites of any cards
    #                     2: [1, 4],  # cid=2 is a prerequisite of 1
    #                     3: [1, 2],  # cid=3 is a prerequisite of 1 and 2
    #                     4: []}      # cid=2 is not a prerequisite of any cards

    @beartype
    def __init__(self,
                 cids: list[Cid],
                 prereq_provider: Callable[[Cid], list[Cid]],
                 new_card_position_provider: Callable[[Cid], int]):
        """
        cids: a list of card ids
        prereq_provider: function that maps each cid to a list of its prerequisites (also given as cids)
        new_card_position_provider: function that maps each cid to a number, defining the order that cids
                                    are introduced.
        """
        if type(cids) is not list:
            raise ValueError(f'cids was a {type(cids)} instead of a list')

        # Sort the cid's based on values given by the new_card_position_provider function.
        cids = sorted(cids, key=new_card_position_provider)
        self.cids = cids

        # Create a dictionary containing entries in the form {cid: [list of prerequisite cids]}
        self.requirement_graph = {cid: prereq_provider(cid) for cid in cids}

        # Initialize self.dependents_graph to a dictionary containing each cid as a key and an empty list
        # for each value...
        self.dependents_graph = {cid: [] for cid in self.requirement_graph.keys()}
        # ...then, for each key 'required_cid' populate the corresponding list with the cid's that have 'required_cid'
        # as a prerequisite.
        for cid, required_cids in self.requirement_graph.items():
            if type(required_cids) is not list:
                raise ValueError(f'prereq_provider return a {type(required_cids)} instead of a list')

            for required_cid in required_cids:
                try:
                    self.dependents_graph[required_cid].append(cid)
                except KeyError as e:
                    raise ValueError(f'The CID={required_cid} was listed as a prerequisite of CID={cid} but was not '
                                     f'included in the list of cids.')

        # Check that the set of keys in the graph dicts are equal to set of values in cids.
        # (i.e., no cids are missing and there are no extra cids.)
        assert(set(self.requirement_graph.keys()) == set(cids))
        assert(set(self.dependents_graph.keys()) == set(cids))

    def sort(self) -> list[Cid]:
        card_queue: list[Cid] = []

        # Define local variables for brevity.
        requirement_graph = self.requirement_graph
        dependents_graph = self.dependents_graph

        # Create a list of the cid keys in requirement_graph so that
        # we can reference the indices.
        requirement_keys = list(self.requirement_graph.keys())

        def add_and_prune(cid, iteration_index):
            # Get the index of cid within the requirement_keys dictionary.
            # On Python 3.7+, dictionaries preserve their insertion order.
            cid_ndx = requirement_keys.index(cid)
            is_upcoming_cid = cid_ndx > iteration_index

            # If cid still has unmet requirements,
            # then it is not ready to be added to the card_queue.
            cid_has_unmet_requirement = len(requirement_graph[cid]) > 0
            if cid_has_unmet_requirement:
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
                # which are stored in dependents_graph[cid].
                for dependents_cid in dependents_graph[cid]:
                    requirement_graph[dependents_cid].remove(cid)
                    add_and_prune(dependents_cid, iteration_index)

        for index, key in enumerate(requirement_graph.keys()):
            add_and_prune(key, index)

        return card_queue
