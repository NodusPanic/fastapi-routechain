# fastapi-routechain

Combine multiple `APIRoute` subclasses for FastAPI — with automatic conflict detection.

## Installation

```bash
pip install fastapi-routechain
```

## The problem

FastAPI's `APIRouter` accepts only a single `route_class`. If you want to use
multiple third-party route classes together (e.g. `DishkaRoute` for DI and
`XmlRoute` for XML support), you'd have to manually create a combined class.

## Usage

### `ChainedAPIRouter` — drop-in replacement for `APIRouter`

```python
from fastapi_routechain import ChainedAPIRouter
from dishka.integrations.fastapi import DishkaRoute
from fastapi_xml import XmlRoute

router = ChainedAPIRouter(
    route_classes=[DishkaRoute, XmlRoute],  # priority = list order (MRO)
)

@router.get("/hello")
def hello():
    return {"hello": "world"}
```

### `combine_routes` — just the factory

```python
from fastapi import APIRouter
from fastapi_routechain import combine_routes

MyRoute = combine_routes(DishkaRoute, XmlRoute)

router = APIRouter(route_class=MyRoute)
```

## Priority and MRO

The order of classes in `route_classes` is the priority order — it directly maps
to Python's MRO (Method Resolution Order). The first class wins on conflicts.

```python
# DishkaRoute.__init__ takes priority over XmlRoute.__init__
combine_routes(DishkaRoute, XmlRoute)
```

## Conflict detection

`fastapi-routechain` warns you when combining classes that will silently lose
functionality — e.g. two classes that both override `get_route_handler` without
calling `super()`.

```python
# emits RouteConflictWarning
combine_routes(XmlRoute, SomeOtherHandlerRoute)

# raises RouteConflictError instead
combine_routes(XmlRoute, SomeOtherHandlerRoute, strict=True)
```

You can also check conflicts manually:

```python
from fastapi_routechain import check_conflicts

issues = check_conflicts(RouteA, RouteB, RouteC)
for issue in issues:
    print(issue)
```

## API

| Symbol | Description |
|---|---|
| `ChainedAPIRouter` | `APIRouter` subclass accepting `route_classes` list |
| `combine_routes(*classes, strict=False)` | Returns a combined `APIRoute` subclass |
| `check_conflicts(*classes)` | Returns list of conflict description strings |
| `RouteConflictWarning` | Warning class emitted on soft conflicts |
| `RouteConflictError` | Exception raised in strict mode |
