"""Unit tests for ``prerequisites`` module."""
import beyondki.prerequisites as pre

# pylint: disable=use-implicit-booleaness-not-comparison


def test_extract_prerequisite_tags():
    """Are all prerequisites extracted from tag lists?"""
    assert pre.extract_prerequisite_tags("a") == []
    assert pre.extract_prerequisite_tags("a b") == []
    assert pre.extract_prerequisite_tags("pre:a") == ["a"]
    assert pre.extract_prerequisite_tags("pre:a b") == ["a"]
    assert pre.extract_prerequisite_tags("pre:a pre:b") == ["a", "b"]
    assert pre.extract_prerequisite_tags(" pre:a ") == ["a"]
