"""Module defining different types of agents"""

from abc import ABC, abstractmethod
from collections import deque
from typing import Any, Generic, TypeVar

from kala.models.memory_rules import MemoryRuleT
from kala.models.properties import PropertiesT, SaverProperties
from kala.models.traits import SaverTraits, TraitsT
from kala.utils.misc import universally_unique_identifier


class BaseAgent(
    ABC,
    Generic[TraitsT, PropertiesT, MemoryRuleT],
):
    """
    Base agent meant to be subclassed.

    Attributes
    ----------
    uuid : int | str
        A unique identifier for the agent.
    update_rule : MemoryRuleT | None
        The rule used to decide whether the agent should change their saver
        status depending on the outcome of the previous matches (default is None).

    Methods
    -------
    get_property()
    get_trait()
    update()
    reset()

    """

    _traits: TraitsT
    _properties: PropertiesT
    uuid: int | str
    update_rule: MemoryRuleT | None

    def __init__(
        self,
        traits: TraitsT,
        properties: PropertiesT,
        uuid: int | str,
        update_rule: MemoryRuleT | None = None,
    ) -> None:
        self._traits = traits
        self._properties = properties
        self.uuid = uuid
        self.update_rule = update_rule

    def __hash__(self):
        return hash(self.uuid)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(uuid='{self.uuid}')"

    def __repr__(self) -> str:
        out = f"{str(self)[:-1]}, "
        for k, v in self._traits.to_dict().items():
            if v is not None and k not in ("min_consumption", "min_specialization"):
                out += f"{k}={v}, "
        return out[:-2] + ")>"

    # pylint: disable=protected-access
    def get_property(self, property_name: str) -> Any:
        """
        Get a property value (returns None for an invalid name).

        Parameters
        ----------
        property_name : str
            The name of the property.

        Returns
        -------
        Any

        """
        return getattr(self._properties, property_name)

    # pylint: disable=protected-access
    def get_trait(self, trait_name: str) -> Any:
        """
        Get a trait value (returns None for an invalid name).

        Parameters
        ----------
        trait_name : str
            The name of the trait.

        Returns
        -------
        Any

        """
        return getattr(self._traits, trait_name)

    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        """Play one round of the game."""

    @abstractmethod
    def reset(self) -> None:
        """Reset the agent to starting values."""


AgentT = TypeVar("AgentT", bound=BaseAgent)
"""Used to refer to BaseAgent as well as its subclasses."""


class InvestorAgent(BaseAgent):
    """
    Investor agent.

    Methods
    -------
    update()
    get_savings()
    reset()

    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        is_saver: bool,
        group: int | None = None,
        min_specialization: float = 0.0,
        income_per_period: float = 1.0,
        homophily: float | None = None,
        update_rule: MemoryRuleT | None = None,
        uuid: int | str | None = None,
        rng: int | None = None,
    ):
        """Initialise new investor agent.

        Parameters
        ----------
        is_saver : bool
            Boolean indicating whether the agent is a saver or not.
        group : int
            Optional group (handy to keep track for example of SBM clusters).
        min_specialization : float
            The minimum specialization (default is 0.0).
        income_per_period : float
            The income per period (default is 1.0).
        homophily : float | None
            The homophily of the agent (default is None), if passed should be a
            number between [0, 1].
        update_rule: MemoryRuleT | None
            The rule used to decide whether the agent should change their saver
            status depending on the outcome of the previous matches (default is None).
        uuid : int | str | None
            The unique identifier of the agent (default is None and a random string
            is generated).
        rng : int | None
            The seed used to initialise random generators (default is None).
        """

        uuid = universally_unique_identifier(rng=rng) if uuid is None else uuid

        traits = SaverTraits(
            group=group,
            min_consumption=0,  # not being used
            min_specialization=min_specialization,
            homophily=homophily,
        )

        props = SaverProperties(
            is_saver=is_saver,
            savings=0.0,  # all agents initialised with zero savings
            income_per_period=income_per_period,
            memory=deque([], maxlen=update_rule.memory_length) if update_rule is not None else None,
        )

        super().__init__(
            traits=traits,
            properties=props,
            update_rule=update_rule,
            uuid=uuid,
        )

    def update(self, *args, **kwargs) -> None:
        self._properties.update(*args, update_rule=self.update_rule, uuid=self.uuid, **kwargs)

    def reset(self) -> None:
        self._properties.reset()

    def flip_saver_property(self) -> None:
        """Flip the is_saver property."""
        self._properties.flip_saver_property()

    def get_savings(self) -> float:
        """Handy direct access to property savings."""
        return self.get_property("savings")

    def is_saver(self) -> bool:
        """Handy direct access to property is_saver."""
        return self.get_property("is_saver")
