# Python-Generics

![Unittests status badge](https://github.com/Hochfrequenz/python-generics/workflows/Unittests/badge.svg)
![Coverage status badge](https://github.com/Hochfrequenz/python-generics/workflows/Coverage/badge.svg)
![Linting status badge](https://github.com/Hochfrequenz/python-generics/workflows/Linting/badge.svg)
![Black status badge](https://github.com/Hochfrequenz/python-generics/workflows/Formatting/badge.svg)

Ever wondered how to do something like this?
    
```python
from typing import Generic, TypeVar

T = TypeVar("T")

class MySuperClass(Generic[T]):
    def get_my_type(self) -> type[T]:
        return T  # This does not work

class MySubType(MySuperClass[str]):
    def use_my_type(self):
        my_type = self.get_my_type()  # This should return str
        assert isinstance("Hello", my_type)
```

This package provides functionalities to resolve this issue i.e. to
determine the values of generic type variables in Python.
As of now, it only supports two functions: `get_type_vars` and `get_filled_type`.
These functions work also with pydantic generic models (only tested with pydantic > v2.3.0).
They also work with [PEP 695](https://peps.python.org/pep-0695/) generic types.

The package has no dependencies itself.

## Installation
The package is [available on PyPI](https://pypi.org/project/python-generics/):
```bash
pip install python-generics
```

## How to use (in your own application)

The `get_type_vars` function returns a tuple of all type variables for a given generic type. The `TypeVar`s are
determined by `Generic` if the type is a subclass of `Generic`. Otherwise, they are determined by the indexed
supertypes (the order of the returned tuple is the lexicographical in the list of the supertypes).

```python
from typing import Generic, TypeVar
from generics import get_type_vars

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

class A(Generic[T, U]):
    pass

class B(A[T, U], Generic[U, T]):
    pass

class C(B[T, U], A[T, V]):
    pass

assert get_type_vars(A) == (T, U)
assert get_type_vars(B) == (U, T)
assert get_type_vars(C) == (T, U, V)
```

The `get_filled_type` function determines for a single `TypeVar` the value if defined somewhere.
To determine the value, you have to pass a type or an instance of a type that is a subclass of a generic type
of which you want to determine the value of the `TypeVar`.

Instead of supplying the `TypeVar` itself, you can define the integer position of the `TypeVar` in the tuple of
`TypeVar`s of the generic type.

```python
from typing import Generic, TypeVar
from generics import get_filled_type

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

class A(Generic[T, U]):
    pass

class B(A[str, U]):
    pass

assert get_filled_type(A[str, U], A, T) == str
assert get_filled_type(B[int](), A, 0) == str
```

The `get_filled_type` function is especially useful if you have generic super types in which you want to determine
the value of a `TypeVar` inside methods.

```python
from typing import Generic, TypeVar, Any
from generics import get_filled_type

T = TypeVar("T")

class MySuperType(Generic[T]):
    def get_type(self) -> Any:
        return get_filled_type(self, MySuperType, 0)

class MySubType(MySuperType[str]):
    pass

assert MySubType().get_type() == str
```

## Limitations
Due to how generics are implemented in Python, it is not possible to 
determine the value of a `TypeVar` inside the constructor. This would require
some stack trace analysis and is currently not implemented in this project.
However, for most scenarios there is an easy workaround for this.

What does not work:
```python
from generics import get_filled_type

class MySuperType[T]:
    def __init__(self):
        self.my_type = get_filled_type(self, MySuperType, 0)
        # This will raise a TypeError with something like
        # "The value of the TypeVar is undefined"
_ = MySuperType[str]()
```

But instead, you can do this:
```python
from generics import get_filled_type

class MySuperType[T]:
    def __init__(self):
        self._my_type: type[T] | None = None
    
    @property
    def my_type(self) -> type[T]:
        if self._my_type is None:
            self._my_type = get_filled_type(self, MySuperType, 0)
        return self._my_type

instance = MySuperType[str]()
assert instance.my_type is str
```
Note that the property will only resolve _after_ the constructor has been called i.e. the
object has been created. You cannot use it inside the constructor.

## How to use this Repository on Your Machine (as a developer)

Follow the instructions in our [Python template repository](https://github.com/Hochfrequenz/python_template_repository#how-to-use-this-repository-on-your-machine).

## Contribute

You are very welcome to contribute to this template repository by opening a pull request against the main branch.
