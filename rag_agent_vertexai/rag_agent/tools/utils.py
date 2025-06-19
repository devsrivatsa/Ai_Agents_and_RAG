import logging
import re
import os

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from ..config import Config

logger = logging.getLogger(__name__)

config = Config().config_dict()

def get_corpus_resource_name(corpus_name: str) -> str:
    """
    Convert a corpus name to its full resource name if needed.
    Handles various input formats and ensures the returned name follows Vertex AI's requirements.

    Args:
        corpus_name (str): The corpus name or display name

    Returns:
        str: The full resource name of the corpus
    """
    logger.info(f"Converting corpus name '{corpus_name}' to resource name")

    #If its already a full resource name with the projects/locations/ragCorpora format
    #projects/{PROJECT_ID}/locations/{LOCATION_ID}/ragCorpora/{CORPUS_ID}
    #projects/myProject/locations/us-central1/ragCorpora/myCorpus
    if re.match(r"^projects/[^/]+/locations/[^/]+/ragCorpora/[^/]+$", corpus_name):
        return corpus_name
    #check if this is a display name of an existing corpus
    try:
        #list all existing corpora
       corpora = rag.list_corpora()
       for corpus in corpora:
           if hasattr(corpus, "display_name") and corpus.display_name == corpus_name:
               return corpus.name

    except Exception as e:
        logger.warning(f"Error checking if corpus '{corpus_name}' exists: {str(e)}")
        pass

    # If it contains partial path elements, extract just the corpus id
    if "/" in corpus_name:
        corpus_id = corpus_name.split("/")[-1]
    else:
        corpus_id = corpus_name
    
    #remove any special characters that might cause issues
    corpus_id = re.sub(r"[^a-zA-Z0-9_-]", "_", corpus_id)

    # Get project_id from config, environment, or use default
    project_id = config.get('project_id') or os.getenv('GOOGLE_CLOUD_PROJECT') or os.getenv('GCP_PROJECT')
    if not project_id:
        # If no project ID is available, we'll let Vertex AI handle it
        # This might cause issues, but it's better than failing completely
        logger.warning("No project ID found in config or environment variables")
        project_id = "your-project-id"  # This will likely cause an error, but it's better than crashing
    
    location = config.get('location', 'us-central1')

    #construct the full resource name
    return f"projects/{project_id}/locations/{location}/ragCorpora/{corpus_id}"


def check_corpus_exists(corpus_name: str, tool_context: ToolContext) -> bool:
    """
    Check if a corpus with the given name exists.

    Args:
        corpus_name (str): The name of the corpus to check
        tool_context (ToolContext): The tool context for state management

    Returns:
        bool: True if the corpus exists, False otherwise
    """
    #check state if tool_context is provided
    if tool_context.state.get(f"corpus_exists_{corpus_name}"):
        return True
    
    try:
        #Get the full resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        #check if the corpus exists
        corpora = rag.list_corpora()
        for corpus in corpora:
            if (corpus.name == corpus_resource_name or corpus.display_name == corpus_name):
                #update state
                tool_context.state[f"corpus_exists_{corpus_name}"] = True
                #Also set the current corpus if not already set
                if not tool_context.state.get("current_corpus"):
                    tool_context.state["current_corpus"] = corpus_name
                return True
        return False
    except Exception as e:
        logger.warning(f"Error checking if corpus '{corpus_name}' exists: {str(e)}")
        pass

def set_current_corpus(corpus_name: str, tool_context: ToolContext):
    """
    Set the current corpus in the tool context.

    Args:
        corpus_name (str): The name of the corpus to set as current
        tool_context (ToolContext): The tool context for state management
    """
    #check if the corpus exists
    if check_corpus_exists(corpus_name, tool_context):
        tool_context.state["current_corpus"] = corpus_name
        return True
    
    return False