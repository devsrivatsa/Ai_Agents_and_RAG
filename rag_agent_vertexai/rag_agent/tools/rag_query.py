import logging
from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext
from vertexai import rag
from ..config import Config
from .utils import check_corpus_exists, get_corpus_resource_name

config = Config().config_dict()
logger = logging.getLogger(__name__)

def rag_query(corpus_name: str, query: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Query a Vertex AI RAG corpus with a user question and return relevant information.

    Args:
        corpus_name (str): The name of the corpus to query. If empty, the current corpus will be used.
                          Preferably use the resource_name from list_corpora results.
        query (str): The text query to search for in the corpus
        tool_context (ToolContext): The tool context

    Returns:
        Dict[str, Any]: The query results and status
    """
    try:
        #Check if corpus exists
        if not check_corpus_exists(corpus_name, tool_context):
            return {
                "status": "error",
                "message": f"Corpus '{corpus_name}' does not exist",
                "corpus_name": corpus_name,
                "query": query,
            }
        #Get the corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        #configure retrieval params
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=config["top_k"],
            filter=rag.Filter(vector_distance_threshold=config["distance_threshold"]),
        )
        #perform the query
        logger.info(f"Querying corpus '{corpus_name}' with query:\n{query}\n")
        response = rag.retrieval_query(
            rag_resource=[
                rag.RagResource(rag_corpus=corpus_resource_name),
            ],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )
        #process the response into a more usable format
        results = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx_group in response.contexts.contexts:
                result = {
                    "source_uri":(ctx_group.source_uri if hasattr(ctx_group, "source_uri") else ""),
                    "source_name":(ctx_group.source_display_name if hasattr(ctx_group, "source_display_name") else ""),
                    "text": ctx_group.text if hasattr(ctx_group, "text") else "",
                    "score": ctx_group.score if hasattr(ctx_group, "score") else 0,
                }
                results.append(result)
        
        #if no results, 
        if not results:
            return {
                "status": "warning",
                "message": f"No relevant information found in the corpus {corpus_name} for query:\n{query}\n",
                "corpus_name": corpus_name,
                "query": query,
                "results": [],
                "results_count": len(results)
            }
        #return the results
        return {
            "status": "success",
            "message": f"Successfully queried corpus {corpus_name}",
            "query": query,
            "corpus_name": corpus_name,
            "results": results,
            "results_count": len(results),
        }
    
    except Exception as e:
        error_msg = f"Error querying corpus {corpus_name}: {str(e)}"
        logging.error(error_msg)
        
        return {
            "status": "error",
            "message": error_msg,
            "query": query,
            "corpus_name": corpus_name,
        }
