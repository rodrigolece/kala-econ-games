"""Tests the traits module."""

import pytest

from kala.models.traits import SaverTraits


@pytest.fixture
def simple_saver_traits():
    """Saver trait with no homophily."""
    return SaverTraits(
        group=0,
        min_consumption=1,
        min_specialization=0.1,
        # homophily=0.5,
    )


def test_init_and_conversion_to_dict(simple_saver_traits):
    """Test init and .to_dict() method."""
    st = simple_saver_traits

    st_dict = st.to_dict()
    assert st.group == 0
    assert st_dict["group"] == st.group
    assert st.min_consumption == 1
    assert st_dict["min_consumption"] == st.min_consumption
    assert st.min_specialization == 0.1
    assert st_dict["min_specialization"] == st.min_specialization
