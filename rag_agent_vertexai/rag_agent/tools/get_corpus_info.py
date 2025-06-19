from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext
from vertexai import rag
from ..config import Config
from .utils import get_corpus_resource_name, check_corpus_exists

def get_corpus_info(corpus_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Get detailed information about a specific RAG corpus, including its files.

    Args:
        corpus_name (str): The full resource name of the corpus to get information about.
                           Preferably use the resource_name from list_corpora results.
        tool_context (ToolContext): The tool context

    Returns:
        Dict[str, Any]: Information about the corpus and its files
    """
    try:
        if not check_corpus_exists(corpus_name, tool_context):
            return {
                "status": "error",
                "message": f"Corpus '{corpus_name}' does not exist",
                "corpus_info": None,
            }
        #get the full resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        #Try to get the corpus info
        corpus_display_name = corpus_name
        file_details = []
        try:
            files = rag.list_files(corpus_resource_name) #there is atleast one file in the corpus as the corpus exists.
            for rag_file in files:
                try:
                    file_id = rag_file.name.split("/")[-1]
                    file_info = {
                        "file_id": file_id,
                        "display_name": rag_file.display_name if hasattr(rag_file, "display_name") else "",
                        "source_uri": rag_file.source_uri if hasattr(rag_file, "source_uri") else "",
                        "created_time": str(rag_file.created_at) if hasattr(rag_file, "created_at") else "",
                        "updated_time": str(rag_file.updated_at) if hasattr(rag_file, "updated_at") else "",
                    }
                    file_details.append(file_info)
                except Exception as e:
                    #continue without file details
                    pass
        except Exception as e:
            #continue without file details
            pass
        return {
            "status": "success",
            "message": f"Successfully retrieved information for corpus '{corpus_name}'",
            "corpus_name": corpus_name,
            "corpus_display_name": corpus_display_name,
            "file_count": len(file_details),
            "files": file_details,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting information for corpus '{corpus_name}': {str(e)}",
            "corpus_name": corpus_name,
        }
    