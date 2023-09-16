"""
This module contains functions to determine generic parameters and arguments.
Currently, this module only works for real types, i.e. something like
>>> get_filled_type(List[int], List, 0)
will not work. This is because these "primitive" types are different from "normal" generic types and currently there
is no need to support this edge case.
"""
from typing import Any, Generic
from typing import GenericAlias as TypesGenericAlias  # type: ignore[attr-defined]
from typing import Optional, Protocol, TypeGuard, TypeVar
from typing import _GenericAlias as TypingGenericAlias  # type: ignore[attr-defined]
from typing import get_args, get_origin


class GenericType(Protocol):
    """
    A protocol for generic types. It is used internally to satisfy mypy since it is not smart enough to understand
    that if a type is a subclass of a `_GenericAlias` that it will have this dunder field.
    """

    __orig_bases__: tuple[type, ...]


def get_type_vars(type_: type | GenericType) -> tuple[TypeVar, ...]:
    """
    For a given generic type, return a tuple of its type variables. The type variables are collected through the
    supertypes arguments `Generic` if present.
    If the TypeVars are declared 'inderectly', e.g. like
    >>> class A(GenericType1[T], GenericType2[U, V]):
    then the type variables are collected from all the supertypes from `__orig_bases__`.

    The order is the same as in `Generic` or in lexicographic order of the supertypes arguments if `Generic` is not
    present. Lexicographic order is explained in the documentation of mypy:
    https://mypy.readthedocs.io/en/stable/generics.html#defining-subclasses-of-generic-classes
    Returns an empty tuple if the type is not generic.

    Example:
    >>> T = TypeVar("T")
    >>> U = TypeVar("U")
    >>> V = TypeVar("V")
    >>> class A(Generic[T, U]):
    ...     pass
    ...
    >>> class B(Generic[T, V]):
    ...     pass
    ...
    >>> class C(A[T, U], B[T, V]):
    ...     pass
    ...
    >>> get_type_vars(C)
    (T, U, V)
    """
    if hasattr(type_, "__pydantic_generic_metadata__"):
        return type_.__pydantic_generic_metadata__["parameters"]

    if not _generic_metaclass_executed_on_type(type_):
        return ()

    for base in type_.__orig_bases__:
        if get_origin(base) is Generic:
            return get_args(base)

    # if we get here, the type has not `Generic` directly as supertype. Therefore, collect the type variables from
    # all the supertypes arguments.
    type_vars: list[TypeVar] = []
    for base in type_.__orig_bases__:
        if isinstance(base, (TypingGenericAlias, TypesGenericAlias)):
            for arg in get_args(base):
                if isinstance(arg, TypeVar) and arg not in type_vars:
                    type_vars.append(arg)

    return tuple(type_vars)


def _generic_metaclass_executed_on_type(type_: type | GenericType) -> TypeGuard[GenericType]:
    """
    This function determines if the type was processed by a `_GenericAlias` with all its `__mro_entries__` magic.
    I.e. if the type has `Generic` as supertype or something like `A[T]` in its supertypes.
    """
    if not isinstance(type_, type) or not hasattr(type_, "__orig_bases__"):
        return False

    orig_bases_set = set(
        get_origin(orig_base) if isinstance(orig_base, (TypingGenericAlias, TypesGenericAlias)) else orig_base
        for orig_base in type_.__orig_bases__
    )
    orig_bases_set.discard(None)
    return orig_bases_set == set(type_.__bases__)
    # If the type has generic ancestors, the __orig_bases__ is set by the ancestors at least. I.e. if the type
    # did not redeclare the type variables the generic machinery would not reassign the __orig_bases__. Therefore,
    # if the origins of __orig_bases__ are not a subset of the __bases__ then the type did not redeclare the type
    # variables.


def _find_super_type_trace(type_: type, search_for_type: type) -> Optional[list[type]]:
    """
    This function returns a list of ancestors tracing from `type_` to `search_for_type`.
    The list is ordered from `type_` to `search_for_type`. If `search_for_type` is not a supertype of
    `type_`, `None` is returned.
    """
    if type_ == search_for_type:
        return [type_]
    if type_ == object:
        return None
    for base in type_.__bases__:
        super_type_trace = _find_super_type_trace(base, search_for_type)
        if super_type_trace is not None:
            return [type_] + super_type_trace
    return None


def _process_inputs_of_get_filled_type(
    type_or_instance: Any, type_var_defining_super_type: type, type_var_or_position: TypeVar | int
) -> tuple[type, type, int]:
    """
    This function processes the inputs of `get_filled_type`. It returns a tuple of the filled type, the super type and
    the position of the type var in the supertype. Note, that there don't have to be an actual TypeVar implemented.
    It should also work for types like `list` or `dict`.
    """
    if not isinstance(type_or_instance, (type, TypingGenericAlias, TypesGenericAlias)):
        if hasattr(type_or_instance, "__orig_class__"):
            filled_type = type_or_instance.__orig_class__
        else:
            filled_type = type(type_or_instance)
    else:
        filled_type = type_or_instance
    if not isinstance(type_var_defining_super_type, type):
        raise TypeError(f"Expected a type, got {type_var_defining_super_type!r}")
    if isinstance(type_var_or_position, TypeVar):
        try:
            type_var_index = get_type_vars(type_var_defining_super_type).index(type_var_or_position)
        except ValueError as error:
            raise TypeError(
                f"TypeVar {type_var_or_position!r} is not defined in {type_var_defining_super_type!r}"
            ) from error
    else:
        type_var_index = type_var_or_position

    return filled_type, type_var_defining_super_type, type_var_index


# pylint: disable=too-many-branches, too-many-locals
def get_filled_type(
    type_or_instance: Any, type_var_defining_super_type: type, type_var_or_position: TypeVar | int
) -> Any:
    """
    Determines the type of the `type_var_or_position` defined by the type `type_var_defining_super_type`.
    The value of the type var is determined using `type_or_instance`.
    This can be an instance or a type, but it must have `type_var_defining_super_type` as a supertype.
    >>> T = TypeVar("T")
    >>> class A(Generic[T]):
    ...     pass
    ...
    >>> get_filled_type(A[int], A, T)
    int
    >>> get_filled_type(A[int], A, 0)
    int
    """
    filled_type, type_var_defining_super_type, type_var_index = _process_inputs_of_get_filled_type(
        type_or_instance, type_var_defining_super_type, type_var_or_position
    )

    # Now iterate through the types ancestors to trace the type_var and eventually find the provided type.
    # If the type_var is not found, raise an error.
    filled_type_origin = (
        get_origin(filled_type) if isinstance(filled_type, (TypingGenericAlias, TypesGenericAlias)) else filled_type
    )
    type_trace = _find_super_type_trace(filled_type_origin, type_var_defining_super_type)
    if type_trace is None:
        raise TypeError(f"Type {filled_type!r} is not a subtype of {type_var_defining_super_type!r}")

    for reversed_index, type_ in enumerate(reversed(type_trace[:-1]), start=2):
        if hasattr(type_, "__pydantic_generic_metadata__"):
            if len(type_.__pydantic_generic_metadata__["args"]) > 0:
                type_var_replacement = type_.__pydantic_generic_metadata__["args"][type_var_index]
                if not isinstance(type_var_replacement, TypeVar):
                    return type_var_replacement
                type_var_index = type_.__pydantic_generic_metadata__["parameters"].index(type_var_replacement)
            # Note: In case for pydantic generic models the overwritten __class_get_item__ method returns a child class
            # instead of dealing with __mro_entries__ and __orig_bases__. Therefore, the indexed elements appear as
            # separate elements in the type_trace. We are skipping those "doubled" elements if they contain no
            # information about `args`.
            # Note also that pydantic does not create a child class if the indexed element is the same as the parent.
            # But that would mean that it would not contain any information about `args` so it is ok to skip those as
            # well.
            continue
        if not _generic_metaclass_executed_on_type(type_):
            raise TypeError(f"Could not determine the type in {filled_type!r}: {type_!r} is not generic")
        for orig_base in type_.__orig_bases__:
            if get_origin(orig_base) == type_trace[-reversed_index + 1]:
                orig_base_args = get_args(orig_base)
                if len(orig_base_args) < type_var_index:
                    raise TypeError(
                        f"Could not determine the type in {filled_type!r}: "
                        f"{orig_base!r} has not enough type arguments"
                    )
                type_var_replacement = orig_base_args[type_var_index]
                if not isinstance(type_var_replacement, TypeVar):
                    return type_var_replacement
                type_var_index = get_type_vars(type_).index(type_var_replacement)
                break

    if not isinstance(filled_type, (TypingGenericAlias, TypesGenericAlias)):
        # Note: Pydantic models which have the type var undefined will also enter this branch
        raise TypeError(f"Could not determine the type in {filled_type!r}: The value of the TypeVar is undefined")

    filled_type_args = get_args(filled_type)
    if len(filled_type_args) < type_var_index:
        raise TypeError(
            f"Could not determine the type in {filled_type!r}: " f"{filled_type!r} has not enough type arguments"
        )

    return filled_type_args[type_var_index]
