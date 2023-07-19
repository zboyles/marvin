import hashlib
import inspect
import re
from datetime import datetime
from functools import lru_cache
from typing import Callable, Union
from zoneinfo import ZoneInfo

import tiktoken
from jinja2 import (
    ChoiceLoader,
    Environment,
    StrictUndefined,
    pass_context,
    select_autoescape,
)
from markupsafe import Markup

import marvin.utilities.async_utils

NEWLINES_REGEX = re.compile(r"(\s*\n\s*)")
MD_LINK_REGEX = r"\[(?P<text>[^\]]+)]\((?P<url>[^\)]+)\)"

jinja_env = Environment(
    loader=ChoiceLoader(
        [
            # PackageLoader("marvin", "prompts")
        ]
    ),
    autoescape=select_autoescape(default_for_string=False),
    trim_blocks=True,
    lstrip_blocks=True,
    auto_reload=True,
    undefined=StrictUndefined,
    enable_async=True,
)

jinja_env.globals.update(
    zip=zip,
    arun=marvin.utilities.async_utils.run_sync,
    now=lambda: datetime.now(ZoneInfo("UTC")),
)


@pass_context
def render_filter(context, value):
    """
    Allows nested rendering of variables that may contain variables themselves
    e.g. {{ description | render }}
    """
    _template = context.eval_ctx.environment.from_string(value)
    result = _template.render(**context)
    if context.eval_ctx.autoescape:
        result = Markup(result)
    return result


jinja_env.filters["render"] = render_filter


def tokenize(text: str) -> list[int]:
    tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return tokenizer.encode(text)


def detokenize(tokens: list[int]) -> str:
    tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return tokenizer.decode(tokens)


def count_tokens(text: str) -> int:
    return len(tokenize(text))


def slice_tokens(text: str, n_tokens: int) -> str:
    tokens = tokenize(text)
    return detokenize(tokens[:n_tokens])


def split_tokens(text: str, n_tokens: int) -> list[str]:
    tokens = tokenize(text)
    return [
        detokenize(tokens[i : i + n_tokens]) for i in range(0, len(tokens), n_tokens)
    ]


def condense_newlines(text: str) -> str:
    def replace_whitespace(match):
        newlines_count = match.group().count("\n")
        if newlines_count <= 1:
            return " "
        else:
            return "\n" * newlines_count

    text = inspect.cleandoc(text)
    text = NEWLINES_REGEX.sub(replace_whitespace, text)
    return text.strip()


def html_to_content(html: str) -> str:
    if marvin.settings.html_parsing_fn is not None:
        if isinstance(marvin.settings.html_parsing_fn, Callable):
            return marvin.settings.html_parsing_fn(html)
        else:
            raise ValueError(
                "`html_parsing_fn` must be a callable, not"
                f" {type(marvin.settings.html_parsing_fn)}"
            )

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # Get text
    text = soup.get_text()

    # Replace multiple newline characters with a single newline
    text = re.sub(r"\n+", "\n", text)

    return text


def convert_md_links_to_slack(text) -> str:
    # converting Markdown links to Slack-style links
    def to_slack_link(match):
        return f'<{match.group("url")}|{match.group("text")}>'

    # Replace Markdown links with Slack-style links
    slack_text = re.sub(MD_LINK_REGEX, to_slack_link, text)

    return slack_text


@lru_cache(maxsize=2048)
def hash_text(*text: str) -> str:
    m = hashlib.sha256()
    for t in text:
        bs = t.encode() if not isinstance(t, bytes) else t
        m.update(bs)
    return m.hexdigest()


def rm_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def rm_text_after(text: str, substring: str) -> str:
    return (
        text[: start + len(substring)]
        if (start := text.find(substring)) != -1
        else text
    )


def split_text(
    text: str,
    chunk_size: int,
    chunk_overlap: float = None,
    last_chunk_threshold: float = None,
    return_index: bool = False,
) -> Union[str, tuple[str, int]]:
    """
    Split a text into a list of strings. Chunks are split by tokens.

    Args:
        text (str): The text to split.
        chunk_size (int): The number of tokens in each chunk.
        chunk_overlap (float): The fraction of overlap between chunks.
        last_chunk_threshold (float): If the last chunk is less than this fraction of
            the chunk_size, it will be added to the prior chunk
        return_index (bool): If True, return a tuple of (chunk, index) where
            index is the character index of the start of the chunk in the original text.
    """
    if chunk_overlap is None:
        chunk_overlap = 0.1
    if chunk_overlap < 0 or chunk_overlap > 1:
        raise ValueError("chunk_overlap must be between 0 and 1")
    if last_chunk_threshold is None:
        last_chunk_threshold = 0.25

    tokens = tokenize(text)

    chunks = []
    for i in range(0, len(tokens), chunk_size - int(chunk_overlap * chunk_size)):
        chunks.append((tokens[i : i + chunk_size], len(detokenize(tokens[:i]))))

    # if the last chunk is too small, merge it with the previous chunk
    if len(chunks) > 1 and len(chunks[-1][0]) < chunk_size * last_chunk_threshold:
        chunks[-2][0].extend(chunks.pop(-1)[0])

    if return_index:
        return [(detokenize(chunk), index) for chunk, index in chunks]
    else:
        return [detokenize(chunk) for chunk, _ in chunks]
