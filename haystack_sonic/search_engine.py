from haystack.backends import BaseSearchBackend


class SonicSearchEngine(BaseSearchBackend):
    def clear(self, models=None, commit=True):
        """Clear all instances of models in sonic database."""
