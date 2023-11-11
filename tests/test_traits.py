"""Tests the traits module."""

import pytest

from kala.models.memory_rules import AverageMemoryRule
from kala.models.traits import SaverTraits


@pytest.fixture
def simple_saver_traits():
    """Saver trait with no homophily."""
    return SaverTraits(
        group=0,
        is_saver=True,
        min_consumption=1,
        min_specialization=0.1,
        updates_from_n_last_games=2,
        # homophily=0.5,
    )


def test_init_and_conversion_to_dict(simple_saver_traits):
    """Test init and .to_dict() method."""
    st = simple_saver_traits

    st_dict = st.to_dict()
    assert st.group == 0
    assert st_dict["group"] == st.group
    assert st.is_saver
    assert st_dict["is_saver"] == st.is_saver
    assert st.min_consumption == 1
    assert st_dict["min_consumption"] == st.min_consumption
    assert st.min_specialization == 0.1
    assert st_dict["min_specialization"] == st.min_specialization


def test_memory_trait(simple_saver_traits):
    """Test the memory trait."""
    st = simple_saver_traits
    rule = AverageMemoryRule()
    st.update(successful_round=1, update_rule=rule)
    st.update(successful_round=2, update_rule=rule)
    st.update(successful_round=3, update_rule=rule)  # this should push out the first value
    assert list(st.memory) == [2, 3]  # type: ignore

    st.update(successful_round=False, update_rule=rule)
    st.update(successful_round=False, update_rule=rule)
    assert not st.is_saver
