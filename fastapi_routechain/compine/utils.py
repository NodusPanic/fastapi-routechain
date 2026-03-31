import inspect

from fastapi.routing import APIRoute

from fastapi_routechain.compine.constants import _CONFLICT_METHODS


def _overrides_without_super(cls: type[APIRoute], method_name: str) -> bool:
    """Check if this class defines the method (not inherited from APIRoute)."""
    return method_name in cls.__dict__


def _uses_super(cls: type[APIRoute], method_name: str) -> bool:
    """
    Heuristic: check if the method source contains 'super()'.
    Returns False (assume no super) if source cannot be inspected.
    """

    try:
        method = cls.__dict__.get(method_name)
        if method is None:
            return True
        source = inspect.getsource(method)
        return "super()" in source
    except (OSError, TypeError):
        return False


def check_conflicts(*route_classes: type[APIRoute]) -> list[str]:
    """
    Returns a list of human-readable conflict descriptions.
 
    A conflict occurs when multiple classes override the same critical method
    without calling super() — meaning only the first in MRO order will win,
    and the rest will be silently ignored.
    """
    issues = []
 
    for method in _CONFLICT_METHODS:
        overriders = [
            cls for cls in route_classes
            if _overrides_without_super(cls, method)
        ]
        if len(overriders) <= 1:
            continue
 
        no_super = [cls for cls in overriders if not _uses_super(cls, method)]
 
        if len(no_super) > 1:
            names = [cls.__name__ for cls in no_super]
            winner = names[0]
            losers = names[1:]
            issues.append(
                f"`{method}` is overridden by {names} without calling super(). "
                f"Only `{winner}` will take effect; {losers} will be silently ignored."
            )
        elif len(no_super) == 1:
            no_super_name = no_super[0].__name__
            with_super = [c.__name__ for c in overriders if _uses_super(c, method)]
            issues.append(
                f"`{method}`: `{no_super_name}` does not call super(), "
                f"but {with_super} do. Correct behaviour depends on MRO order — "
                f"put `{no_super_name}` last in route_classes."
            )
 
    return issues
