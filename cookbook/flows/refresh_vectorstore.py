import re
from datetime import timedelta

import marvin
from marvin.loaders.base import Loader
from marvin.loaders.discourse import DiscourseLoader
from marvin.loaders.github import GitHubRepoLoader
from marvin.loaders.openapi import OpenAPISpecLoader
from marvin.loaders.web import HTMLLoader, SitemapLoader
from marvin.utilities.documents import Document
from marvin.utilities.logging import get_logger as get_marvin_logger
from prefect import flow, task
from prefect.blocks.core import Block
from prefect.logging.loggers import forward_logger_to_prefect
from prefect.tasks import task_input_hash

# Discourse categories
SHOW_AND_TELL_CATEGORY_ID = 26
HELP_CATEGORY_ID = 27

PREFECT_COMMUNITY_CATEGORIES = {
    SHOW_AND_TELL_CATEGORY_ID,
    HELP_CATEGORY_ID,
}


def include_topic_filter(topic) -> bool:
    return (
        "marvin" in topic["tags"]
        and topic["category_id"] in PREFECT_COMMUNITY_CATEGORIES
    )


prefect_loaders = [
    SitemapLoader(
        urls=["https://docs.prefect.io/sitemap.xml"],
        exclude=["api-ref"],
    ),
    OpenAPISpecLoader(
        openapi_spec_url="https://api.prefect.cloud/api/openapi.json",
        api_doc_url="https://app.prefect.cloud/api",
    ),
    HTMLLoader(
        urls=[
            "https://prefect.io/about/company/",
            "https://prefect.io/security/overview/",
            "https://prefect.io/security/sub-processors/",
            "https://prefect.io/security/gdpr-compliance/",
            "https://prefect.io/security/bug-bounty-program/",
        ],
    ),
    GitHubRepoLoader(
        repo="prefecthq/prefect",
        include_globs=["**/*.py"],
        exclude_globs=[
            "tests/**/*",
            "docs/**/*",
            "**/migrations/**/*",
            "**/__init__.py",
            "**/_version.py",
        ],
    ),
    GitHubRepoLoader(
        repo="prefecthq/prefect",
        include_globs=["release-notes.md"],
    ),
    DiscourseLoader(
        url="https://discourse.prefect.io",
        n_topic=500,
        include_topic_filter=include_topic_filter,
    ),
    GitHubRepoLoader(
        repo="prefecthq/prefect-recipes",
        include_globs=["flows-advanced/**/*.py"],
    ),
    SitemapLoader(
        urls=["https://www.prefect.io/sitemap.xml"],
        include=[re.compile("prefect.io/guide/case-studies/.+")],
    ),
]


async def set_chroma_settings():
    """
    the `json/chroma-client-settings` Block should look like this:
    {
        "chroma_server_host": "<chroma server IP address>",
        "chroma_server_http_port": <chroma server port>
    }
    """
    chroma_client_settings = await Block.load("json/chroma-client-settings")

    for key, value in chroma_client_settings.value.items():
        setattr(marvin.settings, key, value)


def html_parser_fn(html: str) -> str:
    import trafilatura

    trafilatura_config = trafilatura.settings.use_config()
    # disable signal, so it can run in a worker thread
    # https://github.com/adbar/trafilatura/issues/202
    trafilatura_config.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")
    return trafilatura.extract(html, config=trafilatura_config)


def keyword_extraction_fn(text: str) -> list[str]:
    import yake

    kw = yake.KeywordExtractor(
        lan="en",
        n=1,
        dedupLim=0.9,
        dedupFunc="seqm",
        windowsSize=1,
        top=10,
        features=None,
    )

    return [k[0] for k in kw.extract_keywords(text)]


@task(
    name="Load Prefect Documents",
    retries=1,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
    task_run_name="Run {loader.__class__.__name__}",
)
async def run_loader(loader: Loader) -> list[Document]:
    return await loader.load()


@flow(name="Update Marvin's Knowledge", log_prints=True)
async def update_marvin_knowledge(topic_name: str | None = None):
    """Flow updating Marvin's knowledge with info from the Prefect community."""
    forward_logger_to_prefect(get_marvin_logger())

    marvin.settings.html_parsing_fn = html_parser_fn
    marvin.settings.keyword_extraction_fn = keyword_extraction_fn

    await set_chroma_settings()

    documents = [
        doc
        for future in await run_loader.map(prefect_loaders)
        for doc in await future.result()
    ]

    print(documents[0])


if __name__ == "__main__":
    import asyncio

    asyncio.run(update_marvin_knowledge())
