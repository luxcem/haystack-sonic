from haystack.backends import (
    BaseEngine,
)
from .search_engine import SonicSearchEngine
from .search_query import SonicSearchQuery

class SonicEngine(BaseEngine):
    backend = SonicSearchEngine
    query = SonicSearchQuery 
