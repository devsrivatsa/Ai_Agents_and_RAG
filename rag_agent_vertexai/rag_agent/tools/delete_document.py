from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext
from vertexai import rag
from .utils import check_corpus_exists, get_corpus_resource_name

def delete_document(corpus_name: str, document_id: str, confirm: bool, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Delete a specific document from a Vertex AI RAG corpus.

    Args:
        corpus_name (str): The full resource name of the corpus containing the document.
                          Preferably use the resource_name from list_corpora results.
        document_id (str): The ID of the specific document/file to delete. This can be
                          obtained from get_corpus_info results.
        confirm (bool): Must be set to True to confirm deletion
        tool_context (ToolContext): The tool context

    Returns:
        Dict[str, Any]: Status information about the deletion operation
    """
    #check if corpus exists
    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"Corpus '{corpus_name}' does not exist",
            "corpus_name": corpus_name,
            "document_id": document_id,
        }
    #check if user wants to confirm deletion
    if not confirm:
        return {
            "status": "error",
            "message": "Deletion not confirmed. Please set confirm to True to proceed.",
            "corpus_name": corpus_name,
            "document_id": document_id,
        }
    try:
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        rag_file_path = f"{corpus_resource_name}/ragFiles/{document_id}"
        rag.delete_file(rag_file_path)

        return {
            "status": "success",
            "message": f"Document '{document_id}' deleted successfully from corpus '{corpus_name}'",
            "corpus_name": corpus_name,
            "document_id": document_id,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error deleting document '{document_id}' from corpus '{corpus_name}': {str(e)}",
            "corpus_name": corpus_name,
            "document_id": document_id,
        }
