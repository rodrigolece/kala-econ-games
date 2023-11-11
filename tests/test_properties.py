"""Test the properties module."""

import pytest

from kala.models.properties import SaverProperties


@pytest.fixture
def simple_saver_properties():
    """Saver properties ."""
    return SaverProperties(savings=0, income_per_period=1)


def test_init_and_conversion_to_dict(simple_saver_properties):
    """Test init and .to_dict() method."""

    sp = simple_saver_properties
    # sp_dict = sp.to_dict() # this wouldn't pass 2nd assert
    sp.update(payoff=1)
    sp.update(payoff=1)
    assert sp.savings == 2

    sp_dict = sp.to_dict()  # NB: dict has copied values, not references
    assert sp_dict["savings"] == sp.savings
