from marvin import ai_fn

from tests.utils.mark import pytest_mark_class


@pytest_mark_class("llm")
class TestAIFunctionMapping:
    def test_mapping_sync(self, prefect_db):
        @ai_fn
        def opposite(thing: str) -> str:
            """returns the opposite of the input"""

        assert opposite.map(["up", "left"]) == ["down", "right"]

    async def test_mapping_async(self, prefect_db):
        @ai_fn
        async def opposite(thing: str) -> str:
            """returns the opposite of the input"""

        assert await opposite.map(["up", "left"]) == ["down", "right"]
