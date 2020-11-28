import elastic_app_search as app_search

from .search import _build_index


def elastic_app_search(
    _,
    search_client,
    pages,
    **search_params,
):
    """Upload the pages to an enterprise app search engine

    Parameters
    ----------
    search_client: elastic_app_search.Client
        Client object to index_documents. Refer to elastic_app_search docs 
        for more info
    pages: list[Page]
        page-like objects to build documents 
    **search_params:
        options to be used to build the document_index
        required params include 'engine', 'fields', and 'id_field'

    Returns
    -------
    index_documents 
        the index_documents method sent to your elastic_app_search Client"""

    documents = [x for x in _build_index(pages=pages, id_field="id", **search_params)]
    return search_client.index_documents(
        engine_name=search_params["engine"],
        documents=documents,
    )
