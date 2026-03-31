from dataclasses import dataclass, field

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi_xml import XmlAppResponse, XmlBody, XmlRoute, add_openapi_extension
from fastapi_routechain import ChainedAPIRouter

from dishka.integrations.fastapi import DishkaRoute, setup_dishka, FromDishka
from dishka import AsyncContainer, make_async_container, Scope, Provider, provide


class DIClass:
    def __init__(self) -> None:
        pass


class DIProvider(Provider):
    scope = Scope.REQUEST
    di = provide(DIClass)


def make_container() -> AsyncContainer:
    return make_async_container(DIProvider())


app = FastAPI(default_response_class=XmlAppResponse)
setup_dishka(make_container(), app)


class TR(APIRoute):
    def get_route_handler(self):
        return super().get_route_handler()


router = ChainedAPIRouter(route_classes=[XmlRoute, DishkaRoute])
add_openapi_extension(app)


@dataclass
class HelloSchema:
    text: str = field(default="", metadata={"name": "text", "type": "Element"})


@dataclass
class HelloResponse:
    text: str = field(default="", metadata={"name": "text", "type": "Element"})
    di: str = field(default="", metadata={"name": "text", "type": "Element"})


@router.post("/hello", response_model=HelloResponse, tags=["Example"])
async def hello(di: FromDishka[DIClass], x: HelloSchema = XmlBody()) -> HelloResponse:
    x.text += " FOO"
    res = HelloResponse(text=x.text, di=str(di))
    return res


app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("example.app:app", host="0.0.0.0", port=8000, reload=True)
