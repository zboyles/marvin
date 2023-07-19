import io
import re
import zipfile
from collections import Counter
from functools import lru_cache
from typing import Callable

import httpx

import marvin


@lru_cache()
def get_stopwords():
    url = "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/stopwords.zip"
    stopwords_file = "stopwords/english"
    response = httpx.get(url)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        with z.open(stopwords_file) as f:
            stopwords = f.read().decode().splitlines()

    return set(stopwords)


def extract_keywords(
    text: str,
    n_keywords: int = 10,
) -> list[str]:
    if marvin.settings.keyword_extraction_fn is not None:
        if isinstance(marvin.settings.keyword_extraction_fn, Callable):
            return marvin.settings.keyword_extraction_fn(text)
        else:
            raise ValueError(
                "`keyword_extraction_fn` must be a callable, not"
                f" {type(marvin.settings.keyword_extraction_fn)}"
            )

    stopwords = get_stopwords()
    words = re.findall(r"\b\w+\b", text.lower())
    filtered_words = [word for word in words if word not in stopwords]
    common_words = Counter(filtered_words).most_common(n_keywords)
    return [word for word, _ in common_words]
