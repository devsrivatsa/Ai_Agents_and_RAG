from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from .utils import check_corpus_exists, get_corpus_resource_name

def delete_corpus(corpus_name: str, confirm: bool, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Delete a Vertex AI RAG corpus when it's no longer needed.
    Requires confirmation to prevent accidental deletion.

    Args:
        corpus_name (str): The full resource name of the corpus to delete.
                           Preferably use the resource_name from list_corpora results.
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
        }
    #check if user wants to confirm deletion
    if not confirm:
        return {
            "status": "error",
            "message": "Deletion not confirmed. Please set confirm to True to proceed.",
            "corpus_name": corpus_name,
        }
    try:
        #get the corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        #delete the corpus
        rag.delete_corpus(corpus_resource_name)
        #remove state tracking
        state_key = f"corpus_exists_{corpus_name}"
        if state_key in tool_context.state:
            tool_context.state[state_key] = False
        
        return {
            "status": "success",
            "message": f"Corpus '{corpus_name}' deleted successfully.",
            "corpus_name": corpus_name,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error deleting corpus '{corpus_name}': {str(e)}",
            "corpus_name": corpus_name, 
        }