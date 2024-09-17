"""Test the properties module."""

from collections import deque

import pytest

from kala.models.memory_rules import AverageMemoryRule
from kala.models.properties import SaverProperties


NUM_GAMES = 2


@pytest.fixture
def simple_saver_properties():
    """Saver properties."""
    return SaverProperties(
        is_saver=True,
        savings=0,
        income_per_period=1,
        memory=None,
    )


@pytest.fixture()
def saver_memoried_properties():
    """Saver properties with memory."""
    return SaverProperties(
        is_saver=True,
        savings=0,
        income_per_period=1,
        memory=deque([], maxlen=NUM_GAMES),
    )


def test_init_and_conversion_to_dict(simple_saver_properties):
    """Test init and .to_dict() method."""

    sp = simple_saver_properties
    # sp_dict = sp.to_dict() # this wouldn't pass 2nd assert
    sp.update(payoff=1)
    sp.update(payoff=1)
    assert sp.savings == 2

    sp_dict = sp.to_dict()  # NB: dict has copied values, not references
    assert sp_dict["savings"] == sp.savings

    assert sp.is_saver
    assert sp_dict["is_saver"] == sp.is_saver


def test_memory_property(saver_memoried_properties):
    """Test the memory property."""
    sp = saver_memoried_properties
    rule = AverageMemoryRule(memory_length=NUM_GAMES)
    # normally the memory would hold booleans but below we test the values contained
    sp.update(successful_round=1, update_rule=rule)
    sp.update(successful_round=2, update_rule=rule)
    sp.update(successful_round=3, update_rule=rule)  # this should push out the first value
    assert list(sp.memory) == [2, 3]  # type: ignore

    sp.update(successful_round=False, update_rule=rule)
    sp.update(successful_round=False, update_rule=rule)
    assert not sp.is_saver
