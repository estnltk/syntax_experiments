from estnltk.storage.postgres import PostgresStorage, IndexQuery
from .base_reader import BaseReader
from estnltk_core.converters.serialisation_registry import SERIALISATION_REGISTRY
from . import syntax_v1


class DbReader(BaseReader):
    __collection = None
    _layers = []

    def set_layers(self, layers):
        """

        """
        self._layers = layers

    def __init__(self, pgpass_file, schema, role, temporary, collection_name, ):
        if 'syntax_v1' not in SERIALISATION_REGISTRY:
            SERIALISATION_REGISTRY['syntax_v1'] = syntax_v1

        super().__init__()
        storage = PostgresStorage(
            pgpass_file=pgpass_file,
            schema=schema,
            role=role,
            temporary=temporary
        )

        self.__collection = storage[collection_name]

    def get_collection_size(self):
        return len(self.__collection)

    def get_all_collections(self):
        self.get_collections()

    def get_collections(self, col_ids=None, shuffle=False, queries=None, count=None, progressbar=None):
        if col_ids is None:
            col_ids = []
        if queries is None:
            queries = []
        q = None
        if len(col_ids):
            q = IndexQuery(col_ids)

        for a_q in queries:
            if q is None:
                q = a_q
            else:
                q = q & a_q

        my_select = self.__collection.select(
            query=q,
            progressbar=progressbar,
            layers=self._layers,
            return_index=True)

        if count and shuffle:
            my_select = my_select.sample(count, amount_type='SIZE')
        elif count and not shuffle:
            my_select = my_select.head(count)
        elif shuffle:
            my_select = my_select.permutate()

        for (colId, text) in my_select:
            yield colId, text
