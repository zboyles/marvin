import asyncio
from typing import Optional

import httpx
from typing_extensions import Literal

import marvin
from marvin.tools import Tool
from marvin.vectorstores.chroma import Chroma

QueryResultType = Literal["documents", "distances", "metadatas"]


async def list_collections() -> list[dict]:
    async with httpx.AsyncClient() as client:
        chroma_api_url = (
            f"http://{marvin.settings.chroma.chroma_server_host}"
            f":{marvin.settings.chroma.chroma_server_http_port}"
        )
        response = await client.get(
            f"{chroma_api_url}/api/v1/collections",
        )

    response.raise_for_status()
    return response.json()


async def query_chroma(
    query: str,
    n_results: int = 5,
    max_characters: int = 2000,
    collection: Optional[str] = None,
    where: Optional[dict] = None,
    where_document: Optional[dict] = None,
    include: Optional[list[QueryResultType]] = None,
) -> str:
    if not include:
        include = ["documents"]

    print(collection)

    async with Chroma(
        collection or marvin.settings.chroma_default_collection
    ) as chroma:
        query_result = await chroma.query(
            query_texts=[query],
            where=where,
            where_document=where_document,
            n_results=n_results,
            include=include,
        )

    return "\n\n".join(
        excerpt for excerpts in query_result["documents"] for excerpt in excerpts
    )[:max_characters]


class QueryChroma(Tool):
    """Tool for querying a Chroma index."""

    description: str = """
        Retrieve document excerpts from a knowledge-base given a query.
    """

    async def run(
        self,
        query: str,
        collection: Optional[str] = None,
        n_results: int = 5,
        where: Optional[dict] = None,
        where_document: Optional[dict] = None,
        include: Optional[list[QueryResultType]] = None,
        max_characters: int = 2000,
    ) -> str:
        return query_chroma(
            query=query,
            n_results=n_results,
            max_characters=max_characters,
            collection=collection,
            where=where,
            where_document=where_document,
            include=include,
        )


class MultiQueryChroma(Tool):
    """Tool for querying a Chroma index."""

    description: str = """
        Retrieve document excerpts from a knowledge-base given a query.
    """

    async def run(
        self,
        queries: list[str],
        collection: Optional[str] = None,
        n_results: int = 5,
        where: Optional[dict] = None,
        where_document: Optional[dict] = None,
        include: Optional[list[QueryResultType]] = None,
        max_characters: int = 3000,
    ) -> str:
        coros = [
            query_chroma(
                query=query,
                n_results=n_results,
                max_characters=max_characters // len(queries),
                collection=collection,
                where=where,
                where_document=where_document,
                include=include,
            )
            for query in queries
        ]
        return "\n\n".join(await asyncio.gather(*coros))
