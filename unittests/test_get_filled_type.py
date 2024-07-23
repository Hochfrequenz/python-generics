"""
A module with unit tests for the `get_filled_type` function.
"""

from typing import Any, Generic, List, TypeVar

import pytest
from pydantic import BaseModel

from generics import get_filled_type


class TestGetFilledType:
    """
    Test `get_filled_type`
    """

    def test_generic_alias_with_type_var(self):
        """
        Test `get_filled_type` by passing a generic alias with a TypeVar directly to the function
        """
        T = TypeVar("T")

        class A(Generic[T]):
            pass

        assert get_filled_type(A[T], A, T) is T

    def test_generic_alias_with_concrete_type(self):
        """
        Test `get_filled_type` by passing a generic alias with a concrete type directly to the function
        """
        T = TypeVar("T")

        class A(Generic[T]):
            pass

        assert get_filled_type(A[int], A, T) is int

    def test_defined_in_super_type(self):
        """
        Test `get_filled_type` with the value for the TypeVar defined in the super type
        """
        T = TypeVar("T")

        class A(Generic[T]):
            pass

        class B(A[int]):
            pass

        assert get_filled_type(B, A, T) is int

    def test_defined_in_super_type_with_deep_inheritance_and_mixtures(self):
        """
        Test `get_filled_type` with deep inheritance structure and mixtures of generic aliases and classes etc.
        """
        T = TypeVar("T")
        U = TypeVar("U")
        Z = TypeVar("Z")

        class A(Generic[T]):
            pass

        class B(A[T]):
            pass

        class C(Generic[U]):
            pass

        class D(B[Z], C[int], List[U], Generic[U, Z]):
            pass

        assert get_filled_type(D[int, str], A, T) is str

    def test_defined_in_instance_of_generic_alias(self):
        """
        Test `get_filled_type` with an instance (created through a _GenericAlias) instead of a type passed to the
        function.
        """
        T = TypeVar("T")

        class A(Generic[T]):
            pass

        a = A[int]()

        assert get_filled_type(a, A, T) is int

    def test_defined_in_instance_of_class(self):
        """
        Test `get_filled_type` with an instance (created through a class) instead of a type passed to the function.
        """
        T = TypeVar("T")

        class A(Generic[T]):
            pass

        class B(A[int]):
            pass

        b = B()

        assert get_filled_type(b, A, T) is int

    def test_defined_in_instance_of_generic_alias_with_deep_inheritance_and_mixtures(self):
        """
        Test `get_filled_type` with an instance instead of a type and with deep inheritance structure and mixtures of
        generic aliases and classes etc.
        """
        T = TypeVar("T")
        U = TypeVar("U")
        Z = TypeVar("Z")

        class A(Generic[T]):
            pass

        class B(A[T]):
            pass

        class C(Generic[U]):
            pass

        class D(B[Z], C[int], List[U], Generic[U, Z]):
            pass

        d = D[int, str]()

        assert get_filled_type(d, A, T) is str

    def test_defined_in_instance_of_generic_alias_with_deep_inheritance_and_mixtures_trough_proxy(self):
        """
        Test `get_filled_type` with an instance instead of a type and with deep inheritance structure and mixtures of
        generic aliases and classes etc. The instance is created through a partially filled type.
        """
        T = TypeVar("T")
        U = TypeVar("U")
        Z = TypeVar("Z")

        class A(Generic[T]):
            pass

        class B(A[T]):
            pass

        class C(Generic[U]):
            pass

        class D(B[Z], C[int], List[U], Generic[U, Z]):
            pass

        E = D[int, T]

        e = E[str]()

        assert get_filled_type(e, A, T) is str

    def test_generic_pydantic_class(self):
        """
        Test `get_filled_type` with a generic pydantic class
        """
        T = TypeVar("T")
        U = TypeVar("U")

        class A(BaseModel, Generic[T, U]):
            a: T

        class B(A[int, U]):
            pass

        assert get_filled_type(A[str, int], A, U) is int
        assert get_filled_type(B, A, T) is int

    def test_generic_with_classes(self):
        """
        Test `get_filled_type` with a class as value for the TypeVar
        """
        T = TypeVar("T")
        U = TypeVar("U")

        class A(Generic[T, U]):
            pass

        class B:
            pass

        class C(A[B, int]):
            pass

        assert get_filled_type(C, A, T) is B

    def test_undefined_type_var(self):
        """
        Test `get_filled_type` with an undefined TypeVar. The function should raise a TypeError.
        """
        T = TypeVar("T")
        U = TypeVar("U")

        class A(Generic[T, U]):
            pass

        class B(A[int, U]):
            pass

        with pytest.raises(TypeError) as error:
            get_filled_type(B, A, U)

        assert "The value of the TypeVar is undefined" in str(error.value)

    def test_pydantic_undefined_type_var(self):
        """
        Test `get_filled_type` with an undefined TypeVar but on a pydantic model. The function should raise a TypeError.
        """
        T = TypeVar("T")
        U = TypeVar("U")

        class A(BaseModel, Generic[T, U]):
            pass

        class B(A[int, U]):
            pass

        with pytest.raises(TypeError) as error:
            get_filled_type(B, A, U)

        assert "The value of the TypeVar is undefined" in str(error.value)

    def test_not_a_subtype(self):
        """
        Test `get_filled_type` with a type that is not a subtype of the super type. The function should raise a
        TypeError.
        """
        T = TypeVar("T")
        U = TypeVar("U")

        class A(Generic[T, U]):
            pass

        class B(Generic[T]):
            pass

        with pytest.raises(TypeError) as error:
            get_filled_type(B[int], A, T)

        assert "is not a subtype" in str(error.value)

    def test_with_self_instance(self):
        """
        Test `get_filled_type` with `self` as instance.
        """
        T = TypeVar("T")

        class MySuperType(Generic[T]):
            # pylint: disable=missing-function-docstring
            def get_type(self) -> Any:
                return get_filled_type(self, MySuperType, 0)

        class MySubType(MySuperType[str]):
            pass

        assert MySubType().get_type() == str

    def test_builtin_list_as_supertype(self):
        """
        Test `get_filled_type` with the builtin list as supertype.
        """

        class A(list[str]):
            pass

        assert get_filled_type(A, list, 0) is str

    def test_builtin_dict(self):
        """
        Test `get_filled_type` with the builtin dict put directly into the function.
        """
        assert get_filled_type(dict[str, int], dict, 1) is int
        assert get_filled_type(dict[str, int], dict, 0) is str
