from enum import StrEnum
from pydantic import BaseModel, validate_arguments, Extra, validator, PrivateAttr
from typing import Optional, Callable, Dict, Any, Union, Literal, Type
import functools
import abc


class Role(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    SYSTEM = "system"


class FunctionCall(BaseModel):
    name: str
    arguments: str


class Message(BaseModel):
    role: Role = Role("user")
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[FunctionCall] = None

    def __init__(self, content: str = None, *args, **kwargs):
        super().__init__(content=content, **kwargs)

    def dict(self, *args, exclude_none=True, **kwargs):
        if self.function_call:
            response = super().dict(*args, **kwargs, exclude_none=exclude_none)
        else:
            response = super().dict(*args, **kwargs, exclude_none=exclude_none)
        return response


class Function:
    @validate_arguments
    def __new__(
        cls, fn: Callable, *args, name: str = None, description: str = None, **kwargs
    ):
        # Apply validation to the function arguments and get a new validated instance
        instance = validate_arguments(fn, config=cls.Config)
        # Enforce a common type for the model
        instance.model = type(
            "BaseFunctionModel",
            (instance.model,),
            {
                **instance.model.__dict__.copy(),
                "name": name or fn.__name__,
                "description": description or fn.__doc__ or "",
                "__fields__": {
                    field_name: field_info
                    for field_name, field_info in instance.model.__fields__.items()
                    if field_name not in ["args", "kwargs", "v__duplicate_kwargs"]
                },
            },
        )

        # Set the schema method of the model to the partial function
        instance.schema = functools.partial(cls._schema, instance)
        instance.parse_raw = functools.partial(cls._parse_raw, instance)

        # Set the name of the model; use the provided name or the name of the function
        instance.model.name = name or fn.__name__

        # Set the description of the model; use the provided description,
        # the docstring of the function, or an empty string
        instance.model.description = description or fn.__doc__ or ""

        return instance

    # Define a method to generate a schema for the function
    def _schema(wrapped_fn, *args, name: str = None, description: str = None, **kwargs):
        # Get the model and function from the wrapped function
        model = wrapped_fn.model

        # Return a dictionary representing the schema
        return {
            "name": name or model.name,
            "description": description or model.description,
            "parameters": model.schema(*args, **kwargs),
        }

    def _parse_raw(wrapped_fn, *args, **kwargs):
        model = wrapped_fn.model
        return wrapped_fn(**model.parse_raw(*args, **kwargs).dict())

    # Define a class for the configuration of the wrapped model
    class Config:
        # Allow the addition of extra fields
        extra = Extra.allow

        # Define a method to modify the schema for the model
        def schema_extra(schema: Dict[str, Any], model: Any) -> None:
            # Remove the title from the schema
            schema.pop("title", None)
            # Remove the title from each property in the schema
            for prop in schema.get("properties", {}).values():
                prop.pop("title", None)


class BaseRequest(BaseModel):
    messages: list[Message] = []
    functions: list[Callable] = None
    function_call: Optional[Union[dict[Literal["name"], str], Literal["auto"]]] = None

    @validator("functions", pre=True, each_item=True)
    def enrich_function(cls, fn):
        return Function(fn)

    def dict(self, *args, exclude_none=True, **kwargs):
        response = super().dict(*args, **kwargs, exclude_none=exclude_none)
        if self.functions is not None:
            response["functions"] = [fn.schema() for fn in self.functions]
        return response


class AbstractResponse(abc.ABC):
    @abc.abstractmethod
    def parse_raw(self):
        pass


class BaseResponse(AbstractResponse, Message):
    function_call: Optional[FunctionCall] = None

    @functools.singledispatchmethod
    def __init__(self, content: Union[str, dict], *args, **kwargs):
        super().__init__(content=content, **kwargs)

    @__init__.register
    def _(self, content: dict):
        params = self.__class__.parse_raw(content)
        super().__init__(**params)


class AbstractChatCompletion(abc.ABC):
    @abc.abstractmethod
    def create(self):
        pass

    @abc.abstractmethod
    async def acreate(self):
        pass


class AbstractState(abc.ABC):
    def __enter__(self):
        print("leeeroyyy")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("jenkins")
        pass


class BaseState(AbstractState, BaseModel):
    complete: Optional[Callable] = None
    turns: list[tuple[BaseRequest, BaseResponse]] = []
    children: list["BaseState"] = []

    @property
    def last_turn(self):
        return next(iter(self.turns[::-1]), (None, None))

    @property
    def last_request(self):
        return self.last_turn[0]

    @property
    def last_response(self):
        return self.last_turn[1]

    @property
    def last_evaluated_response(self):
        if not self.last_response:
            return None
        if not self.last_response.function_call:
            return None

        # Get the function call from the last response
        fn = {fn.model.name: fn for fn in self.last_request.functions}.get(
            self.last_response.function_call.name
        )

        # Parse the arguments of the function call
        result = fn.parse_raw(self.last_response.function_call.arguments)
        print(fn.__name__, fn.model.name)
        return {"name": fn.model.name, "content": result, "role": Role.FUNCTION}

    def messages(self, *args, evaluate_function=True, **kwargs):
        messages = []
        if self.last_request:
            messages += [*self.last_request.messages]
        if self.last_response:
            messages += [self.last_response]
        if self.last_evaluated_response and evaluate_function:
            messages += [Message(**self.last_evaluated_response)]

        return [message.dict() for message in messages]

    def dict(self, *args, **kwargs):
        return super().dict(*args, **kwargs, exclude={"complete"})

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.allow
