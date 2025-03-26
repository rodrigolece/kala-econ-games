# Kala, agent-based econ games


This package defines a general framework to implement different agent-based models (ABMs). One of the most important things that we aim to support is a networked topology, with agents being represented as nodes that can only be matched against their neighbours. However, we also support games that do not include a network topology.

To begin with, we have used the framework to coded the model presented in *Ernst, Ekkehard. ‘The Evolution of Time Horizons for Economic Development’, 2004.*  \[**Ernst04**\] [(DOI)](https://doi.org/10.13140/RG.2.2.34593.15204). We added some extensions, including support for networks.



## Installation

The package is published to [PyPI](https://pypi.org/) and can be installed directly using

```bash
$ pip install kala-econ-games
```


## User guide

The user-facing interface of the package is located under `kala.models` but the concrete classes have been added to the top-level package so that they can be imported directly.

Before going into more detail, we'll give and comment a full example that creates a working game.

We start with some imports

```python
from kala import (
    GamePlan,
    get_gini_coefficient,
    get_saver_agents,
    get_summed_score,
    init_savers_gamestate_from_netz,
    play_game,
    shocks,
)
```
We use [Networkx](https://networkx.org/) to define the network topologies. There are a great deal of real-world networks [the Netzschleuder repository](https://networks.skewed.de/) and these can be downloaded directly and a new game can be initialised using

```python
network_name = "dolphins"
game = init_savers_gamestate_from_netz(network_name, savers_share=0.5, memory_length=4)
agents = game.agents
```

We have implemented some shocks which are defined outside the game, and used as part of a `GamePlan`. A game and a game plan are passed directly to the `play_game` function which is the primary entry point to run the simulations. The game can be inspected directly (note for example the use of `game.agents`) and we provide some functions to retrieve basic statistics.

```python
shocks = {
    4: [shocks.RemovePlayer(agents[2])],
    6: [shocks.SwapRandomEdge()],
}


game_plan = GamePlan(10, shocks=shocks)

for time, state in play_game(game, game_plan):
    savers = get_saver_agents(state)
    num_savers = len(savers)
    total_score = get_summed_score(state.agents)
    saver_score = get_summed_score(savers)
    gini = get_gini_coefficient(state.agents)

    print(f"Time {time}: num_agents={len(state.agents)}; num_savers={num_savers}")
    print(f"\tTotal:  {round(total_score, 2)}")
    print(f"\tSavers: {round(saver_score, 2)}")
    print(f"\tGini:   {round(gini, 3)}")

```

---

More generally, it can be useful to work directly with networks and these can be downloaded and converted to a NetworkX graph using the `NetzDatabase` interface.

```python
from kala import NetzDatabase

db = NetzDatabase()
graph = db.read_netzschleuder_network(network_name)
```


### Agents

Agents should be the starting point of any model. Agents are created by passing arguments that are specific to the model, but that can be broken down into two categories (traits and properties). Once created, an agent should have all of the necessary information to call the `update()` method which for example adds a payoff to the running total of the agent.

In order to implement the models in \[**Ernst04**\], we define the class `SaverAgent`. Typically, one would initialise an instance using the `init_saver_agent` function.

#### Traits and properties

Traits and properties belong to agents. Roughly speaking, traits were thought as fixed and properties as changing in time, but the distinction is no longer clear-cut and in the future we might decide to deprecate one of the two classes.

#### Memory rules

Agents that have a memory can change their properties in response to the interactions they have had in the last turns. We control how they behave using an update or memory rule. We have added support for a single rule at the moment (`SaverFlipAfterFractionLost`) but we plan to add support for more.

### Graphs

We use graphs directly from NetworkX, and we implement an `AgentPlacementNetX` which manages keeps track of where agents are placed in the Graph.


### Strategies

A strategy encodes what two agents should do when they "encounter" and they play each other. The main method exposed is `calculate_payoff()`.

Following \[**Ernst04**\], we coded the class `SaverCooperationPayoffStrategy` which draws payoffs from a log-normal distribution with mean 1.0 and a variance (and therefore risk) that depends on the specialization of each agent.


### Games

A game (or more precisely a GameState) holds all the information of the graph, the agents, etc, at any given point.

The main way to interect with a game is to define a `GamePlan` which defines the number of steps that the game will go on for (and possibly shocks are applied and when), and call `play_game`.


## Contributing

The package is written in Python (minimal version: 3.10).
We recommend that the installation is made inside a virtual environment.
While you can use `conda` or Python's built-in `venv`, we recommend `uv` ([https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)).

### Local install with `uv`

If you don't have `uv` installed, follow the instructions on their [documentation](https://docs.astral.sh/uv/getting-started/installation/).
Once `uv` is installed, navigate to the project's root directory and run:

```bash
$ uv sync
```

This command creates a virtual environment in the `.venv` directory and installs all project dependencies.

You have two options for using the virtual environment:

1. Activate the environment using:

```bash
$ source .venv/bin/activate
```

2. Execute scripts or programs directly within the virtual environment by prefixing your commands with `uv run`:

```bash
$ uv run python my_script.py
$ uv run pytest tests/
```

For more information on using `uv`, please refer to the [official documentation](https://docs.astral.sh/uv/).


#### Local install of the package

Once we are working inside an active virtual environment, we install (the dependencies and) the package by running

```bash
$ pip install -e .
```

### Development Environment

The package uses several tools (linters, formatters, etc.) that automatically run checks and help correct simple problems.
The recommended way to set up your development environment is using `uv`.

To install all development tools and the package, run

```bash
$ uv sync --dev
```

We use [`just`](https://just.systems/man/en/) to manage common development tasks like linting, formatting, and testing.
With `uv` installed, the easiest way to install `just` is via the command

```
$ uv tool install rust-just
```

Once installed, to see all available commands run

```bash
$ just --list
```

### Contributing with code

When contributing code, please create a new branch with a descriptive name, such as `feat/add-super-custom-agent`.

Once you're ready, create a pull request.
We have automated checks that run on every pull request.
Your code _must_ pass these checks before it can be merged.
If the checks fail, update your code and push the changes to re-trigger the checks.
We also recommend requesting a code review from another maintainer before merging.

Before submitting a pull request, it's highly recommended to run the checks locally to catch any issues early.
Run the following command to execute all checks:

```bash
$ just
```

You can format the code automatically by running

```bash
$ just format-all
```

Or only run the test suite with

```bash
just test
```

If the `just` command passes locally, it's highly likely that the automated CI/CD pipeline on GitHub will also pass.
