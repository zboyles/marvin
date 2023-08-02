from abc import ABC
from typing import Callable, Literal, Optional, Type, Union

from marvin.pydantic import BaseModel, Extra, Field, root_validator, validator
from marvin.types import Function


class AbstractChatRequest(BaseModel, ABC):
    messages: list[dict[str, str]] = Field(default_factory=list, merge=True)
    functions: Optional[list[Callable, dict[str, str]]] = None
    function_call: Optional[Union[Literal["auto"], dict[Literal["name"], str]]] = None

    response_model: Optional[Type[BaseModel]] = Field(default=None, exclude=True)
    evaluate_function_call: bool = Field(default=False, exclude=True)

    @root_validator(pre=True)
    def cast_response_model_to_callable(cls, values):
        if values.get("response_model", None):
            fn = Function.from_model(values.get("response_model"))
            values["functions"] = [fn]
            values["function_call"] = {"name": fn.__name__}
        return values

    @validator("functions", each_item=True)
    def cast_callable_to_function_model(cls, fn):
        return Function(fn) if isinstance(fn, Callable) else fn

    class Config:
        extra = Extra.allow
        merge = {"functions", "messages"}
        validate_assignment = True

    @property
    def callable_registry(self):
        return {fn.__name__: fn for fn in self.functions if callable(fn)}

    @property
    def functions_schema(self):
        return [fn.model.schema() if callable(fn) else fn for fn in self.functions]

    def dict(self, *args, exclude_none=True, **kwargs):
        return super().dict(*args, **kwargs, exclude_none=exclude_none)

    def schema(self, *args, **kwargs):
        response = self.dict(*args, **kwargs, exclude={"functions"})
        if self.functions:
            response["functions"] = self.functions_schema
        return response

    def __call__(self, *args, **kwargs):
        for key, value in kwargs.items():
            if key in self.Config.merge:
                setattr(self, key, getattr(self, key) + value)
            else:
                setattr(self, key, value)
        return self
