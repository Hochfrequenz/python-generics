"""
A module with unit tests for the `get_type_vars` function.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

from generics import get_type_vars


class TestGetTypeVars:
    """
    Test `get_type_vars`
    """

    def test_generic_class(self):
        """
        Test `get_type_vars` by passing a plain generic class to the function
        """
        T = TypeVar("T")

        class A(Generic[T]):
            pass

        assert get_type_vars(A) == (T,)

    def test_generic_class_with_multiple_type_vars(self):
        """
        Test `get_type_vars` by passing a generic class with multiple type vars to the function
        """
        T = TypeVar("T")
        U = TypeVar("U")

        class A(Generic[T, U]):
            pass

        assert get_type_vars(A) == (T, U)

    def test_generic_class_with_multiple_type_vars_and_inheritance(self):
        """
        Test `get_type_vars` by passing a generic subclass with multiple type vars to the function. The type vars are
        defined implicitly through indexing without use of `Generic`. The order should be lexicographic.
        """
        T = TypeVar("T")
        U = TypeVar("U")

        class A(Generic[T, U]):
            pass

        class B(A[T, U]):
            pass

        assert get_type_vars(B) == (T, U)

    def test_generic_class_with_multiple_type_vars_and_inheritance_and_additional_type_vars(self):
        """
        Test `get_type_vars` by passing a generic subclass with multiple type vars to the function. The type vars are
        defined explicitly through the usage of `Generic`. The order should be the same as in `Generic`.
        """
        T = TypeVar("T")
        U = TypeVar("U")
        V = TypeVar("V")

        class A(Generic[T, U]):
            pass

        class B(A[T, U], Generic[T, V, U]):
            pass

        assert get_type_vars(B) == (T, V, U)

    def test_generic_class_with_multiple_indirect_type_vars(self):
        """
        Test `get_type_vars` by passing a generic subclass with multiple type vars to the function. The subclass
        inherits from two generic classes with type vars. The type vars are defined implicitly through indexing without
        use of `Generic`. The order should be lexicographic.
        """
        T = TypeVar("T")
        U = TypeVar("U")
        V = TypeVar("V")

        class A(Generic[T, U]):
            pass

        class B(Generic[T, V]):
            pass

        class C(A[T, U], B[T, V]):
            pass

        assert get_type_vars(C) == (T, U, V)

    def test_generic_class_mixed_supertypes(self):
        """
        Test `get_type_vars` by passing a generic subclass with multiple type vars to the function. The subclass also
        inherits from a non-generic class.
        """
        T = TypeVar("T")
        U = TypeVar("U")
        V = TypeVar("V")

        class A(Generic[T, U]):
            pass

        class B(Generic[T, V]):
            pass

        class C:
            pass

        class D(A[T, U], B[T, V], C):
            pass

        assert get_type_vars(D) == (T, U, V)

    def test_generic_class_partially_defined(self):
        """
        Test `get_type_vars` by passing a generic subclass with multiple type vars to the function. The subclass
        defines some of the type vars. Only the undefined type vars should be returned in lexicographic order.
        """
        T = TypeVar("T")
        U = TypeVar("U")
        V = TypeVar("V")

        class A(Generic[T, U]):
            pass

        class B(Generic[T, V]):
            pass

        class C:
            pass

        class D(A[T, str], B[int, V], C):
            pass

        assert get_type_vars(D) == (T, V)

    def test_not_generic(self):
        """
        Test `get_type_vars` by passing a non-generic class to the function. It should return an empty tuple.
        """

        class A:
            pass

        assert get_type_vars(A) == ()

    def test_generic_class_not_redeclared_type_vars(self):
        """
        If a class does not redeclare the type vars in its supertype list it is treated as non-generic. Therefore,
        an empty tuple shall be returned.
        """
        T = TypeVar("T")
        U = TypeVar("U")
        V = TypeVar("V")

        class A(Generic[T, U]):
            pass

        class B(Generic[T, V]):
            pass

        class C(A, B):
            pass

        assert get_type_vars(C) == ()

    def test_generic_pydantic_class(self):
        """
        Test `get_type_vars` against pydantic generic models.
        """
        T = TypeVar("T")
        U = TypeVar("U")

        class A(BaseModel, Generic[T, U]):
            a: T
            b: U

        assert get_type_vars(A) == (T, U)
