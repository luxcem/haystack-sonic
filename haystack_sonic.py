from urllib.parse import urlparse
import logging
from django.core.exceptions import ImproperlyConfigured

from haystack.backends import (
    BaseEngine,
    BaseSearchBackend,
    BaseSearchQuery,
)
from haystack.models import SearchResult
from haystack.exceptions import SkipDocument
from sonic import IngestClient, SearchClient
from haystack.utils.app_loading import haystack_get_model


class SonicSearchEngine(BaseSearchBackend):
    def __init__(self, connection_alias, **connection_options):
        super().__init__(connection_alias, **connection_options)
        if "HOST" not in connection_options:
            raise ImproperlyConfigured(
                "You must specify a 'HOST' in your settings for connection '%s'."
                % connection_alias
            )
        self.host = connection_options["HOST"]
        self.port = str(connection_options.get("PORT", 1491))
        self.password = str(connection_options.get("PASSWORD", ""))
        self.log = logging.getLogger("haystack")
        try:
            with IngestClient(self.host, self.port, self.password) as ingest:
                ingest.ping()
        except ConnectionRefusedError:
            raise ImproperlyConfigured(
                "Sonic is not running on %s:%s" % (self.host, self.port)
            )

    def update(self, index, iterable, commit=True):
        with IngestClient(self.host, self.port, self.password) as ingest:
            for obj in iterable:
                doc = index.full_prepare(obj)
                ingest.push("haystack", "documents", doc["id"], doc["text"])

    def clear(self, models=None, commit=True):
        """Clear all instances of models in sonic database."""
        with IngestClient(self.host, self.port, self.password) as ingest:
            ingest.flush_collection("*")

    def search(self, query_string, **kwargs):
        self.log.debug("SonicEngine.search() query_string=%s" % query_string)
        with SearchClient(self.host, self.port, self.password) as search:
            raw_results = search.query("haystack", "documents", query_string)
            results = []

            for result in raw_results:
                app_label, model_name, pk = result.split(".")
                results.append(SearchResult(app_label, model_name, pk, 0))
            return {
                "results": results,
                "hits": len(results),
            }


class SonicSearchQuery(BaseSearchQuery):
    def build_query_fragment(self, field, filter_type, value):
        return f"{value}"


class SonicEngine(BaseEngine):
    backend = SonicSearchEngine
    query = SonicSearchQuery
