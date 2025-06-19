from typing import List, Dict, Any
from vertexai import rag

def list_corpora() -> Dict[str, Any]:
    """
    List all available Vertex AI RAG corpora.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - status: "success" or "error"
            - message: Description of the result
            - corpora: List of corpus information, each containing:
                - resource_name: The full resource name to use with other tools
                - display_name: The human-readable name of the corpus
                - create_time: When the corpus was created
                - update_time: When the corpus was last updated
    """
    try:
        #list all corpora
        corpora = rag.list_corpora()
        #process corpus information into more usable format
        corpus_info = []
        for corpus in corpora:
            corpus_data = {
                "resource_name": corpus.name,
                "display_name": corpus.display_name,
                "created_time": str(corpus.created_at) if corpus.created_at else "",
                "updated_time": str(corpus.updated_at) if corpus.updated_at else "",
            }
            corpus_info.append(corpus_data)
        return {
            "status": "success",
            "message": "Found {} corpora".format(len(corpus_info)),
            "corpora": corpus_info,
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing corpora: {str(e)}",
            "corpora": [],
        }