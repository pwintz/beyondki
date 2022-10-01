import shutil
import anki.collection
import anki.notes
import prerequisites

from pprint import pprint

collection_file = 'ordered_temp.anki2';
shutil.copyfile('ordered.anki2', collection_file)

col = anki.collection.Collection(collection_file);
# pprint(type(col))
# pprint(dir(col))
# pprint(col.find_cards("chapter_1"))
# pprint(col.find_cards("tag:pre:chapter_1"))
# pprint(col.find_cards("chapter_2"))

all_notes = col.find_notes('');
pprint(all_notes)

# pprint(col.tags.all())

def get_prereq_tags(nid):
    # Get the tags as a single string.
    tags_str = col.get_note(nid).string_tags()
    return prerequisites.extract_prerequisites_tags(tags_str)


note_prerequisites = {item: get_prereq_tags(item) for item in all_notes}


def get_notes_matching_tags(tags) -> list[int]:
    prereq_nids = []
    for tag in tags:
        nids = col.find_notes('tag:' + tag)
        for nid in nids:
            if nid not in prereq_nids:
                prereq_nids.append(nid)
    return prereq_nids


# Create a dict that contains each note id as a key.
# The value for each key is a list of note ids that are prerequisites for the key.
note_graph = {nid: get_notes_matching_tags(tag) for nid, tag in note_prerequisites.items()}
pprint(note_graph)
