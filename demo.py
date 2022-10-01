"""Demo of prerequisite tag extraction."""
import shutil
import pprint as pp
from itertools import chain

from anki.collection import Collection
from beyondki.prerequisites import extract_prerequisite_tags


def get_prereq_tags(col: Collection, nid: int) -> list[str]:
    """Get the tags as a single string."""
    tags_str = col.get_note(nid).string_tags()
    return extract_prerequisite_tags(tags_str)


def get_notes_matching_tags(col: Collection, tags: list[str]) -> set[int]:
    """Get all nids specified as prereqs in any tags in ``tags``."""

    # For each tag, compute the set of all notes with that tag.
    nid_sets = map(lambda t: set(col.find_notes(f"tag:{t}")), tags)

    # Return the union of all the individual sets.
    return set(chain.from_iterable(nid_sets))


def main() -> None:
    """Run the demo."""
    collection_file = "ordered_temp.anki2"
    shutil.copyfile("ordered.anki2", collection_file)
    col = Collection(collection_file)
    all_nids: List[int] = col.find_notes("")

    print(f"Chapter 1 cards: {col.find_cards('chapter_1')}\n")
    print(f"Cards with 'chapter_1' as prereq: {col.find_cards('tag:pre:chapter_1')}\n")
    print(f"Chapter 2 cards: {col.find_cards('chapter_2')}\n")
    print(f"All nids: {all_nids}\n")
    print(f"All tags\n========\n{pp.pformat(col.tags.all())}\n")

    # Map nids to lists of prereq tags.
    prereqs: dict[int, list[str]] = {nid: get_prereq_tags(col, nid) for nid in all_nids}

    # Map nids to prerequisite nids.
    #
    # For example, a pair ``{5: [1, 2, 3]}`` means that the note with nid 5
    # cannot be studied until the notes with nids 1, 2, and 3 have all been
    # studied, i.e. the notes with nids 1, 2, and 3 are prerequisites for the
    # note with nid 5.
    graph = {nid: get_notes_matching_tags(col, tags) for nid, tags in prereqs.items()}
    print(f"Note graph: {graph}")


if __name__ == "__main__":
    main()
