"""PoC prerequisite sorting."""
from typing import List, FrozenSet, Mapping, Tuple, Iterable
from functools import reduce, partial
from dataclasses import dataclass

from immutables import Map

Cid = int


@dataclass(frozen=True, eq=True)
class Card:
    """A orderable card type."""
    cid: Cid
    ord: int
    due: int


Queue = List[Card]
CardMap = Mapping[Card, FrozenSet[Card]]


def prune(
    deps: CardMap,
    state: Tuple[CardMap, Queue],
    i: Card,
) -> Tuple[CardMap, Queue]:
    """Prune dependencies of `i`."""
    reqs, q = state
    if len(reqs[i] > 0):
        return reqs, []

    # Remove `i` from the prerequisites of each dependency `k` and recurse on `k`.
    reqs = reduce(lambda reqs, k: reqs.delete(k).set(k, reqs[k] - {i}), deps[i], reqs)
    prunables: Iterable[Card] = filter(lambda k: k < i, deps[i])
    return reduce(partial(prune, deps), prunables, (reqs, q + [i]))


def main() -> None:
    """Run the program."""
    deps, reqs, cards = Map(), Map(), []
    _, q = reduce(partial(prune, deps), sorted(cards), (reqs, cards))