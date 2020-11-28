from elasticsearch.helpers import bulk

from .search import _build_index


def elasticsearch(
    _,  # called inside a class
    search_client: elasticsearch.Elasticsearch,
    pages,
    **search_params,
):
    """Upload the pages to an elasticsearch index

    Parameters
    ----------
    search: Search-like object
        Search object from site to push to elasticsearch instance
    pages: list[Page]
        page-like objects to build_indexes out of
    **search_params:
        options to be used to build the document_index
        required params include 'index', 'fields', and 'id_field'

    Returns
    -------
    bulk 
        the bulk command sent to your elasticsearch instance"""
    return bulk(
        client=search_client,
        index=search_params["index"],
        actions=(x for x in _build_index(pages=pages, **search_params)),
    )
