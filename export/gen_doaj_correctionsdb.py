# coding: utf-8
import sys
import json
import math
import time
import logging
import argparse
import functools
from urllib import quote

import requests


LOGGER = logging.getLogger(__name__)

MAX_RETRIES = 4

BACKOFF_FACTOR = 1.9

DEFAULT_DOAJ_API_URL="https://doaj.org/api/v1/"

EPILOG = """\
Copyright 2020 SciELO <scielo-dev@googlegroups.com>.
Licensed under the terms of the BSD license. Please see LICENSE in the source
code for more information.
"""

LOGGER_FMT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


class RetryableError(Exception):
    pass


class NonRetryableError(Exception):
    pass


class retry_gracefully:
    """Produz decorador que torna o objeto decorado resiliente às exceções dos
    tipos informados em `exc_list`. Tenta no máximo `max_retries` vezes com
    intervalo exponencial entre as tentativas.
    """

    def __init__(
        self,
        max_retries=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        exc_list=(RetryableError,),
    ):
        self.max_retries = int(max_retries)
        self.backoff_factor = float(backoff_factor)
        self.exc_list = tuple(exc_list)

    def _sleep(self, seconds):
        time.sleep(seconds)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retry = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except self.exc_list as exc:
                    if retry <= self.max_retries:
                        wait_seconds = self.backoff_factor ** retry
                        LOGGER.info(
                            'could not get the result for "%s" with *args "%s" '
                            'and **kwargs "%s". retrying in %s seconds '
                            "(retry #%s): %s",
                            func.__qualname__,
                            args,
                            kwargs,
                            str(wait_seconds),
                            retry,
                            exc,
                        )
                        self._sleep(wait_seconds)
                        retry += 1
                    else:
                        raise

        return wrapper


@retry_gracefully()
def get(url, timeout=2):
    try:
        response = requests.get(url, timeout=timeout)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
        raise RetryableError(exc)
    except (
        requests.exceptions.InvalidSchema,
        requests.exceptions.MissingSchema,
        requests.exceptions.InvalidURL,
    ) as exc:
        raise NonRetryableError(exc)
    else:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            if 400 <= exc.response.status_code < 500:
                raise NonRetryableError(exc)
            elif 500 <= exc.response.status_code < 600:
                raise RetryableError(exc)
            else:
                raise

    return response.content


class DOAJ:
    def __init__(self, api_url=DEFAULT_DOAJ_API_URL):
        self.api_url = api_url

    def search_journals(self, search_query, page=None):
        url = self.api_url + "search/journals/" + quote(search_query)
        if page:
            url += "?page=%s" % page

        return get(url)

    def iter_search_journals(self, search_query):
        results = json.loads(self.search_journals(search_query))
        total_pages = math.ceil(results["total"] / results["pageSize"])

        for journal in results.get("results", []):
            yield journal

        for page in range(2, int(total_pages + 1)):
            results = json.loads(self.search_journals(search_query, page=page))
            for journal in results.get("results", []):
                yield journal


def iter_journals_by_provider(name):
    search_query = 'bibjson.provider:"%s"' % name
    doaj = DOAJ()
    return doaj.iter_search_journals(search_query)


def gen_corrections_db(args):
    for journal in iter_journals_by_provider("scielo"):
        bibjson = journal.get("bibjson", {})
        selected_fields = {
            "doaj_id": journal.get("id"),
            "title": bibjson.get("title"),
            "alternative_title": bibjson.get("alternative_title"),
            "is_active": bibjson.get("active"),
            "provider": bibjson.get("provider"),
            "issns": bibjson.get("identifier"),
        }

        args.output.write(json.dumps(selected_fields) + "\n")


def cli(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Tool to send documents from SciELO to DOAJ.", epilog=EPILOG,
    )
    parser.add_argument("--loglevel", default="")
    subparsers = parser.add_subparsers()

    parser_gen_correctionsdb = subparsers.add_parser(
        "gen-correctionsdb", help="Generate corrections DB from DOAJ API.",
    )
    parser_gen_correctionsdb.add_argument(
        "--output", default=sys.stdout, type=argparse.FileType("w"), required=False,
    )
    parser.set_defaults(func=gen_corrections_db)

    args = parser.parse_args(argv)
    # todas as mensagens serão omitidas se level > 50
    logging.basicConfig(
        level=getattr(logging, args.loglevel.upper(), 999), format=LOGGER_FMT
    )
    try:
        return args.func(args)
    except AttributeError:
        parser.print_usage()


def main():
    try:
        sys.exit(cli())
    except KeyboardInterrupt:
        LOGGER.info("Got a Ctrl+C. Terminating the program.")
        # É convencionado no shell que o programa finalizado pelo signal de
        # código N deve retornar o código N + 128.
        sys.exit(130)
    except Exception as exc:
        LOGGER.exception(exc)
        sys.exit("An unexpected error has occurred: %s" % exc)


if __name__ == "__main__":
    main()
