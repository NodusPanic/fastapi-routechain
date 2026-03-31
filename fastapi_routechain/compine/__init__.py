import warnings

from fastapi.routing import APIRoute

from fastapi_routechain.compine.utils import check_conflicts
from fastapi_routechain.exceptions.core import RouteConflictError, RouteConflictWarning


def combine_routes(
    *route_classes: type[APIRoute],
    strict: bool = False,
) -> type[APIRoute]:
    """
    Combine multiple APIRoute subclasses into one via multiple inheritance.
 
    MRO order = priority order. The first class in the list has the highest priority.
 
    Args:
        *route_classes: APIRoute subclasses to combine. Order matters (MRO).
        strict: If True, raise RouteConflictError on conflicts instead of warning.
 
    Returns:
        A new APIRoute subclass combining all provided classes.
 
    Raises:
        RouteConflictError: If strict=True and conflicts are detected.
        ValueError: If no route classes are provided or classes aren't APIRoute subclasses.
 
    Example:
        MyRoute = combine_routes(DishkaRoute, XmlRoute)
        router = APIRouter(route_class=MyRoute)
    """
    if not route_classes:
        raise ValueError("At least one route class must be provided.")
 
    for cls in route_classes:
        if not (isinstance(cls, type) and issubclass(cls, APIRoute)):
            raise ValueError(
                f"{cls!r} is not a subclass of APIRoute."
            )
 
    if len(route_classes) == 1:
        return route_classes[0]
 
    conflicts = check_conflicts(*route_classes)
    if conflicts:
        message = "Route class conflicts detected:\n" + "\n".join(
            f"  • {c}" for c in conflicts
        )
        if strict:
            raise RouteConflictError(message)
        else:
            warnings.warn(message, RouteConflictWarning, stacklevel=2)
 
    name = "".join(cls.__name__ for cls in route_classes)

    return type(name, route_classes, {})
