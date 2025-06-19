import re
from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext
from vertexai import rag
from ..config import Config
from .utils import check_corpus_exists

config = Config().config_dict()

def create_corpus(corpus_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Create a new Vertex AI RAG corpus with the specified name.

    Args:
        corpus_name (str): The name for the new corpus
        tool_context (ToolContext): The tool context for state management

    Returns:
        Dict[str, Any]: Status information about the operation
    """
    #check if corpus already exists
    if check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"Corpus '{corpus_name}' already exists. Please use a different name.",
            "corpus_name": corpus_name,
            "corpus_created": False,
        }
    try:
        display_name = re.sub(r"[^a-zA-Z0-9_-]", "_", corpus_name)
        #configure embedding model
        embedding_model_config = rag.RagEmbeddingModelConfig(
            vertex_prediction_endpoint=rag.VertexPredictionEndpoint(publisher_model=config["text_embedding_model"])
        )
        #create the corpus
        rag_corpus = rag.create_corpus(
            display_name=display_name,
            backend_config=rag.RagVectorDBConfig(
                rag_embedding_model_config=embedding_model_config,
            ),
        )
        #update state to track corpus existance
        tool_context.state[f"corpus_exists_{corpus_name}"] = True
        #set this as the current corpus
        tool_context.state["current_corpus"] = corpus_name

        return {
            "status": "success",
            "message": f"Corpus '{corpus_name}' created successfully.",
            "corpus_name": rag_corpus.name,
            "display_name": rag_corpus.display_name,
            "corpus_created": True,
        }
    
    except Exception as e:
        
        return {
            "status": "error",
            "message": f"Error creating corpus '{corpus_name}': {str(e)}",
            "corpus_name": corpus_name,
            "corpus_created": False,
        }

