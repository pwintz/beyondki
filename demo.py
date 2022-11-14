"""Demo of prerequisite tag extraction."""
import random
import shutil
import pprint as pp
from collections.abc import Sequence, Iterator
from itertools import chain
from pathlib import Path
from typing import Union

import anki.consts
from anki.collection import Collection
from anki.notes import NoteId
from anki.cards import CardId, Card
from beartype import beartype

import sorting
from beyondki.prerequisites import extract_prerequisite_tags


def get_prereq_tags_from_note(col: Collection, nid: NoteId) -> list[str]:
    """Get the tags as a single string."""
    tags_str = col.get_note(nid).string_tags()

    return extract_prerequisite_tags(tags_str)


# def get_prereq_tags_from_card(col: Collection, cid: CardId) -> list[str]:
#     """Get the tags as a single string."""
#     tags_str = col.get_card(cid).string_tags()
#
#     return extract_prerequisite_tags(tags_str)


def get_notes_matching_tags(col: Collection, tags: list[str]) -> list[NoteId]:
    """Get all nids specified as prereqs in any tags in ``tags``."""

    # Find all of the notes that match any of the tags in the list tags.
    nid_sets = []
    for tag in tags:
        nids = col.find_notes(f"tag:{tag}")
        if nids is None:
            continue
        for nid in nids:
            nid_sets.append(nid)

    # Remove duplicates.
    return list(set(nid_sets))


# @beartype
def nids_to_cids(col: Collection, nids: NoteId) -> Sequence[CardId]:
    if isinstance(nids, int):
        nids = [nids]
    # print(f"nids={nids}")
    return [cid for nid in nids for cid in col.card_ids_of_note(nid)]


class MockNote:
    nid: NoteId
    cids: Sequence[CardId]
    tags: list[str]

    def __init__(self, nid, tags, cids):
        self.nid = nid
        self.tags = tags
        self.cids = cids

    def string_tags(self):
        return self.tags

    @staticmethod
    def make_random(tags: str = "", n_cards: int = 1):
        nid = NoteId(random.randrange(1_000_000, 9_999_999))
        cids = [random.randrange(1_000_000, 9_999_999) for i in range(n_cards)]
        return MockNote(nid, tags, cids)


class MockCard:
    nid: NoteId
    cid: CardId
    due: int

    def __init__(self, nid: NoteId, cid: CardId, due: int):
        self.nid = nid
        self.cid = cid
        self.due = due

    def description(self):
        return f"nid={self.nid}, cid={self.cid}, due={self.due}"


class MockCollection:
    @beartype
    def __init__(self, notes: list[MockNote]):
        self.notes_dict: dict[NoteId, MockNote] = {note.nid: note for note in notes}
        self.card_dict: dict[CardId, MockCard] = {cid: MockCard(cid) for note in notes for cid in note.cids}
        self.notes: list[MockNote] = notes
        self.cards: list[CardId] = [cid for note in notes for cid in note.cids]

    def find_notes(self, query: str) -> Iterator[NoteId]:
        if len(query) == 0:
            return self.notes_dict
        result = []
        query_parts = query.split(" ")
        for query_part in query_parts:
            assert query_part.startswith('tag:')  # Only support searching for one tag at a time.
            for note in self.notes:
                if len([tag for tag in note.tags.split(" ") if 'tag:' + tag == query]):
                    result.append(note.nid)
                    continue
        return result

    def find_cards(self, query: str) -> Iterator[CardId]:
        if len(query) == 0:
            return self.cards
        else:
            raise ValueError("Query not supported for find_cards")

    def card_ids_of_note(self, nid):
        return self.notes_dict[nid].cids

    def get_note(self, nid: NoteId) -> MockNote:
        return self.notes_dict[nid]

    def get_card(self, cid: CardId) -> Union[MockCard, Card]:
        return self.card_dict[cid]

    def update_card(self, card):
        pass


def reorder_cards(col: Union[MockCollection, Collection], ordered_cids: Sequence[CardId]) -> None:
    for i, cid in enumerate(ordered_cids):
        card = col.get_card(cid)
        if card.type == anki.consts.CARD_TYPE_NEW:
            card.due = i
            col.update_card(card)


def main() -> None:
    """Run the demo."""
    src_file = "collection.anki2"
    # Hard-coded path to my test collection. TODO: read from options file or command line.
    collection_file = Path(Path.home(), 'AppData', 'Roaming', 'Anki2', 'Test 2', 'collection.anki2')
    shutil.copyfile(src_file, collection_file)

    col = Collection(str(collection_file))

    all_nids: Iterator[NoteId] = col.find_notes("")
    all_cids: Iterator[CardId] = col.find_cards("")
    print(f"all_cids={all_cids}")

    note_tag_prerequisites: dict[NoteId, list[str]] = {nid: get_prereq_tags_from_note(col, nid) for nid in all_nids}
    note_prereqs_graph = {nid: get_notes_matching_tags(col, tags) for (nid, tags) in note_tag_prerequisites.items()}
    card_prereqs_graph = {cid: nids_to_cids(col, note_prereqs_graph[nid])
                          for nid in note_tag_prerequisites.keys() for cid in nids_to_cids(col, nid)}

    ordered_cids = sorting.sort(all_cids, lambda cid: card_prereqs_graph[cid], lambda cid: cid)
    print(f"ordered_cids: {ordered_cids}")

    reorder_cards(col, ordered_cids)

    for i, cid in enumerate(col.find_cards("")):
        card = col.get_card(cid)
        # card.due = i
        print(f"card={card.description()}")

    col.save()
    return

    # # Create a mock collection for easier testing.
    # note1 = MockNote.make_random(tags='tag1 tag2', n_cards=3)
    # note2 = MockNote.make_random(tags='pre:tag1 tag2', n_cards=1)
    # note3 = MockNote.make_random(tags='pre:tag2 tag3', n_cards=1)
    # notes = [note2, note1, note3]
    #
    # col = MockCollection(notes)
    # notes = col.find_notes('tag:tag1')
    # print(notes)
    #
    # all_nids: Iterator[NoteId] = col.find_notes("")
    # all_cids: Iterator[CardId] = col.find_cards("")
    #
    # # print(f"note:{col.get_note(all_nids[0])}")
    #
    # # print(f"Chapter 1 cards: {col.find_cards('chapter_1')}\n")
    # # print(f"Cards with 'chapter_1' as prereq: {col.find_cards('tag:pre:chapter_1')}\n")
    # # print(f"Chapter 2 cards: {col.find_cards('chapter_2')}\n")
    # # print(f"All nids: {all_nids}\n")
    # # print(f"All tags\n{pp.pformat(col.tags.all())}\n")
    #
    # # Map nids to lists of prereq tags.
    # note_tag_prerequisites: dict[NoteId, list[str]] = {nid: get_prereq_tags_from_note(col, nid) for nid in all_nids}
    # note_prereqs_graph = {nid: get_notes_matching_tags(col, tags) for (nid, tags) in note_tag_prerequisites.items()}
    # print(f"note_prereqs_graph: {note_prereqs_graph}")
    #
    # card_prereqs_graph = {cid: nids_to_cids(col, note_prereqs_graph[nid])
    #                       for nid in note_tag_prerequisites.keys() for cid in nids_to_cids(col, nid)}
    #
    # # card_tag_prereqs_graph: dict[CardId, list[str]] = {cid: get_prereq_tags_from_card(col, cid) for cid in all_cids}
    # print(f"card_prereqs_graph: {card_prereqs_graph}")
    # # card_prereqs_graph = dict()
    # # for nid in note_tag_prerequisites.keys():
    # #     print(f"nid={nid}, prereqs={note_tag_prerequisites[nid]}")
    # #     cids: Sequence[CardId] = col.card_ids_of_note(nid)
    # #     prereq_cids = [col.card_ids_of_note(prereq_nid) for prereq_nid in note_tag_prerequisites[nid]]
    # #     print(f"cids={cids}")
    # #     card_prereqs_graph.update({cid: prereq_cids for cid in cids})
    # # print(f"all_nids: {all_nids}")
    # # print(f"all_cids: {all_cids}")
    # card_queue = sorting.sort(all_cids, lambda cid: card_prereqs_graph[cid], lambda cid: cid)
    # print(f"card_queue: {card_queue}")
    #
    # # Map nids to prerequisite nids.
    # #
    # # For example, a pair ``{5: [1, 2, 3]}`` means that the note with nid 5
    # # cannot be studied until the notes with nids 1, 2, and 3 have all been
    # # studied, i.e. the notes with nids 1, 2, and 3 are prerequisites for the
    # # note with nid 5.
    # # graph = {nid: get_notes_matching_tags(col, tags) for nid, tags in note_tag_prerequisites.items()}
    # # print(f"Note graph: {graph}")


if __name__ == "__main__":
    main()
