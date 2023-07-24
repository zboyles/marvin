from functools import partial
from typing import Callable, Literal, Optional, TypeVar, Union

from openai import ChatCompletion as OpenAIChatCompletion
from pydantic import BaseModel

from marvin import settings
from marvin.types import (
    AbstractChatCompletion,
    BaseRequest,
    BaseResponse,
    BaseState,
    Message,
)


class OpenAIRequest(BaseRequest):
    model: str = "gpt-3.5-turbo"
    api_key: str = settings.openai.api_key.get_secret_value()


class OpenAIResponse(BaseResponse):
    @classmethod
    def parse_raw(cls, content: dict):
        message = content.choices[0].message.to_dict()
        function_call = getattr(content.choices[0].message, "function_call", None)
        return {**message, "function_call": function_call}


class OpenAIState(BaseState):
    pass


RequestType = TypeVar("RequestType", bound=OpenAIRequest)
ResponseType = TypeVar("ResponseType", bound=OpenAIResponse)
StateType = TypeVar("StateType", bound=OpenAIState)


def has_no_function_call(State: OpenAIState) -> bool:
    if State.last_response is None:
        return True
    elif State.last_response.function_call is None:
        return False
    else:
        return True


class ChatCompletion(OpenAIChatCompletion, AbstractChatCompletion):
    def __new__(cls, *args, typed=True, **kwargs):
        config = cls.Config()

        default_params = config.request_type(**kwargs)

        subclass = type(
            cls.__name__,
            (cls,),
            {
                "__defaults__": default_params,
                "__functions__": default_params.functions,
                "state": config.state_type,
                "stop_condition": config.stop_condition,
                "request": config.request_type,
                "response": config.response_type,
                "create": partial(super().create, **default_params.dict()),
                "acreate": partial(super().acreate, **default_params.dict()),
            },
        )
        return subclass

    @classmethod
    def complete(
        cls,
        *args,
        State: Optional[StateType] = None,
        messages: list[Message] = [],
        functions: list[Callable] = None,
        function_call: Optional[
            Union[dict[Literal["name"], str], Literal["auto"]]
        ] = None,
    ) -> StateType:
        with State or cls.state() as State:
            request = cls.request(
                messages=messages, functions=functions, function_call=function_call
            )

            State.turns.append((request, cls.response(cls.create(**request.dict()))))

            State.complete = partial(
                cls.complete,
                State=State,
                messages=State.messages(),
                functions=functions,
                function_call=function_call,
            )
            return State

    @classmethod
    def chain(
        cls,
        *args,
        messages: list[Message] = [],
        functions: list[Callable] = None,
        function_call: Optional[
            Union[dict[Literal["name"], str], Literal["auto"]]
        ] = None,
    ) -> StateType:
        State = cls.complete(
            messages=messages, functions=functions, function_call=function_call
        )

        return State

    class Config(BaseModel):
        request_type: RequestType = OpenAIRequest
        response_type: ResponseType = OpenAIResponse
        state_type: StateType = OpenAIState
        stop_condition: Callable[StateType, bool] = has_no_function_call
