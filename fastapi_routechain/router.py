from collections.abc import Callable, Sequence
from enum import Enum
from typing import Any

from fastapi import APIRouter
from fastapi.datastructures import Default
from fastapi.params import Depends
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute
from starlette.types import ASGIApp, Lifespan

from fastapi_routechain.compine import combine_routes


class ChainedAPIRouter(APIRouter):
    """
    A drop-in replacement for FastAPI's APIRouter that accepts multiple
    route classes and combines them automatically.

    Args:
        route_classes: List of APIRoute subclasses to combine (priority = list order).
        strict: If True, raise on route class conflicts instead of warning.

    Example:
        router = ChainedAPIRouter(
            route_classes=[DishkaRoute, XmlRoute],
        )

        # equivalent to:
        router = APIRouter(
            route_class=combine_routes(DishkaRoute, XmlRoute),
        )
    """

    def __init__(
        self,
        *,
        prefix: str = "",
        tags: list[str | Enum] | None = None,
        route_classes: list[type[APIRoute]] | None = None,
        strict: bool = False,
        dependencies: Sequence[Depends] | None = None,
        default_response_class: type[Response] = Default(JSONResponse),
        responses: dict[int | str, dict[str, Any]] | None = None,
        callbacks: list[BaseRoute] | None = None,
        routes: list[BaseRoute] | None = None,
        redirect_slashes: bool = True,
        default: ASGIApp | None = None,
        dependency_overrides_provider: Any | None = None,
        on_startup: Sequence[Callable[[], Any]] | None = None,
        on_shutdown: Sequence[Callable[[], Any]] | None = None,
        lifespan: Lifespan[Any] | None = None,
        deprecated: bool | None = None,
        include_in_schema: bool = True,
        generate_unique_id_function: Callable[[APIRoute], str] = Default(
            generate_unique_id
        ),
        **kwargs: Any,
    ):
        if route_classes:
            if "route_class" in kwargs:
                raise ValueError(
                    "Cannot use both `route_class` and `route_classes`. "
                    "Use `route_classes` only."
                )
            kwargs["route_class"] = combine_routes(*route_classes, strict=strict)

        super().__init__(
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            dependency_overrides_provider=dependency_overrides_provider,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            lifespan=lifespan,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            generate_unique_id_function=generate_unique_id_function,
            **kwargs,
        )
