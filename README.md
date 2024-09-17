# Kala, agent-based econ games


This package defines a general framework to implement different agent-based models (ABMs). One of the most important things that we aim to support is a networked topology, with agents being represented as nodes that can only be matched against their neighbours. However, we also support games that do not include a network topology.

To begin with, we have used the framework to coded the model presented in *Ernst, Ekkehard. ‘The Evolution of Time Horizons for Economic Development’, 2004.*  \[**Ernst04**\] [(DOI)](https://doi.org/10.13140/RG.2.2.34593.15204). We added some extensions, including support for networks.



## Installation

The package is written in Python (minimal version: 3.10). We recommend that the installation is made inside a virtual environment and to do this, one can use either `conda` (recommended in order to control the Python version) or the Python builtin `venv` (if the system's version of Python is compatible).

### Create a virtual environment using Python's builtin `venv`

The first step is running

```bash
$ python -m venv kala
```

This creates a folder that contains the virtual environment `kala` (a different name can be used; change below as appropriate). We activate it using


```bash
$ source kala/bin/activate
```

### Using conda (recommended)

The tool `conda`, which comes bundled with Anaconda has the advantage that it lets us specify the version of Python that we want to use. Python>=3.10 is required.

A new environment can be created with

```bash
$ conda create -n kala python=3.10 -y
```

Like before, the environment's name can be anything else instead of `kala` (simply change the name below). We activate it using

```bash
$ conda activate kala
```

### Local install of the package

Once we are working inside an active virtual environment, we install (the dependencies and) the package by running

```bash
[$ pip install -r requirements.txt]
$ pip install -e .
```

### Coming soon

In the future, we would like to completely package the code and publish it in [PyPI](https://pypi.org/) so that a local installation isn't needed any more, and the installation can be solved directly by the package manager of choice.


## User guide

The user-facing interface of the package is located under `kala.models` but the concrete classes have been added to the top-level package so that they can be imported directly.

Before going into more detail, we'll give and comment a full example that creates a working game.

We start with 3 imports

```python
import networkx as nx
from kala import InvestorAgent, CooperationStrategy, DiscreteTwoByTwoGame, SimpleGraph
```

We've imported [Networkx](https://networkx.org/) as a handy tool to create a pre-defined network from which we "steal" the edges, but other ways of creating graph topologies will be supported in the future.

The first step is defining the agents.

```python
num_nodes = 10

# A list of InvestorAgents, half of them savers and half non-savers
is_saver = savers = [True, False] * 5
agents = [InvestorAgent(is_saver=is_saver[i]) for i in range(num_nodes)]
```

Next, we create a network (with NetworkX) and we instantiate our own `SimpleGraph` which can take a NetworkX object as argument. We also pass the agents so that there is a one-to-one mapping between the nodes in the graph and the individual agents.

```python
g = nx.barabasi_albert_graph(num_nodes, 8, seed=0)
G = SimpleGraph(g, nodes=agents)
```

We initialise a strategy

```python
coop = CooperationStrategy(
    stochastic=True,  # True to draw random numbers
    differential_efficient=0.5,  # eta_hat_hat = 1 + differential_efficient
    differential_inefficient=0.05,  # eta_hat = 1 - differential_inefficient
    rng=0,  # this seeds the random number generator (not needed in general)
)
```

and then we combine the graph (which already encompasses the agents) and the strategy into a game.

```python
game = DiscreteTwoByTwoGame(G, coop)
```

All we need to do now is call a method and, if we want, keep track of different properties like so:

```python
for _ in range(10):
    game.play_round()
    wealth, num_savers = game.get_total_wealth(), game.get_num_savers()
    print(f"wealth={wealth:.2f}, {num_savers=}")
```

---

More complicated configurations can be added in several places. For example, we can create agents that have memory, an update rule, and some amount of homophily by calling


```python
from kala import FractionMemoryRule

agents = [
    InvestorAgent(
        is_saver=is_saver[i],
        update_rule=FractionMemoryRule(fraction=0.75, memory_length=5),
        homophily=0.8
    )
    for i in range(num_nodes)
]
```



### Agents

Agents should be the starting point of any model. Agents are created by passing arguments that are specific to the model, but that can be broken down into two categories (traits and properties). Once created, an agent should have all of the necessary information to call the `update()` method which for example adds a payoff to the running total of the agent.

In order to implement the models in \[**Ernst04**\], we define the class `InvestorAgent` which takes the following arguments:

- `is_saver`: Boolean indicating whether the agent is a saver or not. This trait is important because it will influence the payoff that our agent will get once they play an opponent that can have the same trait or not.
- `homophily`: Normally, agents are paired using the topology of a graph in which they are the nodes. The homophily is an optional probability (a number between [0, 1]) which controls whether agents should preferentially select opponents with the same trait or avoid them entirely.
- `update_rule`: A rule which codifies what the agent should do with the outcome of previous `memory_length` (`n`) games. Normally, an agent records whether their payoff has been smaller than that of its opponent, so they might decide to change their saver trait after loosing half of the `n` games, or all `n` games.


#### Traits and properties

Traits and properties belong to agents. Roughly speaking, traits were thought as fixed and properties as changing in time, but the distinction is no longer clear-cut and in the future we might decide to deprecate one of the two classes.

#### Memory rules

Rules also belong to agents. They handle all the logic of deciding whether the agent should flip its saving strategy based on the past `n` games. The following rules are available (ordered from simplest to most general):

- `AnyPastMemoryRule`
- `AllPastMemoryRule`
- `AverageMemoryRule`
- `FractionMemoryRule`
- `WeightedMemoryRule`

A description of the rules will follow shortly.

### Graphs

Agents are initialised and organised inside a `SimpleGraph` which encodes the topology, that is, the connections of agents. For the time being, the connections are fixed but in the future this can easily be extended so that edges can be re-wired as a game progresses.

### Strategies

A strategy encodes what two agents should do when they "encounter" and they play each other. The main method exposed is `calculate_payoff()`.

Following \[**Ernst04**\], we coded the class `CooperationStrategy` which draws payoffs from a log-normal distribution with mean 1.0 and a variance (and therefore risk) that depends on the specialization of each agent. The specialization depends the two values:

- `differential_inefficient`: When a saver meets a non-saver, their specialization is set to `1 - differential_inefficient` which in the paper's notation is $\hat{\eta}$.
- `differential_efficient`:  When two savers play each other, they decide to cooperate and they select a higher specialization set to `1 + differential_efficient` ($\hat{\hat{\eta}}$ in the paper).

### Games

A game is defined by the graph (which itself already contains initialised agents) and the strategy. It handles the logic of matching two (or more) opponents calculating and distributing the payoffs. The most important method is `play_round()`, but there are also convenient methods to get summaries such as `get_total_wealth()` or `get_num_savers()`.

In order to implement the models \[**Ernst04**\], we use `DiscreteTwoByTwoGame`.

## Contributing

The package has a couple of utilities (linters, formatters, etc.) that automatically run checks and help correct simple problems.

To run on new contributions, use

```bash
$ pre-commit run --all-files
```

You might find it useful to create an alias, for example `alias pcr='pre-commit run --all-files`.


### Extending the existing models

In all cases, we define a base class which can be extended easily to define new models. For example, one could define a new set of agent "traits" like so:

```python
class MyNewTraits(BaseAgentTraits):
    color: str
    age: int
    is_tall: bool
```

When possible, we have have strived to make all such sub-classes interoperable meaning that other parts of the code tend not to assume any functionality other than the one specified in the base class (there are exceptions to this but are working on getting around them).
