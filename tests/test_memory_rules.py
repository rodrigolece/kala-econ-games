"""Test the memory rules module."""

from kala.models.memory_rules import (
    AllPastMemoryRule,
    AnyPastMemoryRule,
    AverageMemoryRule,
    FractionMemoryRule,
)


def test_average_memory_rule():
    rule = AverageMemoryRule(memory_length=4)
    assert not rule.should_update([True, False])
    assert not rule.should_update([True, False, False, False])
    assert rule.should_update([True, False, True, False])


def test_fraction_memory_rule():
    rule = FractionMemoryRule(memory_length=4, fraction=1.0)
    assert not rule.should_update([True, True, True])
    assert not rule.should_update([True, True, True, False])
    assert rule.should_update([True, True, True, True])


def test_all_past_memory_rule():
    rule = AllPastMemoryRule(memory_length=4)
    assert not rule.should_update([True, True, True])
    assert not rule.should_update([True, True, True, False])
    assert rule.should_update([True, True, True, True])


def test_any_past_memory_rule():
    rule = AnyPastMemoryRule(memory_length=2)
    assert not rule.should_update([True])
    assert not rule.should_update([False, False])
    assert rule.should_update([True, False])
