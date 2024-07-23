"""
Tests for Python 3.12 features.
"""

from generics import get_filled_type


class TestPy312:
    """
    Tests for Python 3.12 features
    """

    def test_get_filled_type_with_pep695_generics(self):
        """
        Test `get_filled_type` with PEP 695 generics syntax.
        https://peps.python.org/pep-0695/
        """

        class A[T]:
            pass

        class B[T](A[T]):
            pass

        class C[T]:
            pass

        class D[U, Z](B[Z], C[int], list[U]):
            pass

        assert get_filled_type(D[int, str], A, 0) is str
