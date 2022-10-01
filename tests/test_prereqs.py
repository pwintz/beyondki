import pytest
import prerequisites as pre


def test_is_prerequisites_tag():
    assert pre.is_prerequisites_tag('pre:')
    assert not pre.is_prerequisites_tag('tag:definition')
    assert pre.is_prerequisites_tag('pre:') is True


def test_strip_pre_prefix():
    assert pre.strip_pre_prefix('pre:a') == 'a'
    assert pre.strip_pre_prefix('pre:abc') == 'abc'


def test_extract_prerequisites_tags():
    assert pre.extract_prerequisites_tags('a') == []
    assert pre.extract_prerequisites_tags('a b') == []
    assert pre.extract_prerequisites_tags('pre:a') == ['a']
    assert pre.extract_prerequisites_tags('pre:a b') == ['a']
    assert pre.extract_prerequisites_tags('pre:a pre:b') == ['a', 'b']
    assert pre.extract_prerequisites_tags(' pre:a ') == ['a']
