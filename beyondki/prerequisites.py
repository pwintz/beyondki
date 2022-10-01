def is_prerequisites_tag(tag: str) -> str:
    return tag.startswith('pre:')

def strip_pre_prefix(prereq_tag: str) -> str:
    assert is_prerequisites_tag(prereq_tag)
    return prereq_tag[4:]

def extract_prerequisites_tags(tags_str: str) -> list[str]:
    # Convert to list.
    tags = tags_str.strip().split(' ')
    prereq_tags = list(filter(is_prerequisites_tag, tags))
    prereq_tags = list(map(strip_pre_prefix, prereq_tags))

    return prereq_tags
