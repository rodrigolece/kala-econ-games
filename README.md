# Kala, agent-based econ games


## Installation and contributing

We will work inside a virtual environment. The first step is running

```bash
$ python -m venv venv
```

This creates a folder that contains the virtual environment `venv`. We activate it using


```bash
$ source venv/bin/activate
```

and we install (the dependencies and) the package using

```bash
[$ pip install -r requirements.txt]
$ pip install -e .
```

### Contributions

The package has a couple of utilities (linters, formatters, etc.) that automatically run checks and help correct simple problems.

To run on new contributions, use

```bash
$ pre-commit run --all-files
```

You might find it useful to create an alias, for example `alias pcr='pre-commit run --all-files`.


## Logic of the package

### Traits and properties

New traits can be added by subclassing the `BaseAgentTraits` class like so

```python
class MyNewTraits(BaseAgentTraits):
    color: str
    age: int
    boolean_flag: bool
```

Properties are similar to traits, but the idea is that this will normally be changing. They are built in a similar fashion, but in addition they must implement the `update()` method,


```python
class MyNewProperties(BaseProperties):
    money_in_the_bank: int
    salary: int

    def update(self):
        self.money_in_the_bank += self.salary
```
