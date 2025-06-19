import re
from typing import List, Dict, Any
from google.adk.tools.tool_context import ToolContext
from vertexai import rag
from ..config import Config
from .utils import check_corpus_exists, get_corpus_resource_name

config = Config().config_dict()



def add_data(corpus_name: str, paths: List[str], tool_context: ToolContext) -> Dict[str, Any]:
    """
    Add new data sources to a Vertex AI RAG corpus.

    Args:
        corpus_name (str): The name of the corpus to add data to. If empty, the current corpus will be used.
        paths (List[str]): List of URLs or GCS paths to add to the corpus.
                          Supported formats:
                          - Google Drive: "https://drive.google.com/file/d/{FILE_ID}/view"
                          - Google Docs/Sheets/Slides: "https://docs.google.com/{type}/d/{FILE_ID}/..."
                          - Google Cloud Storage: "gs://{BUCKET}/{PATH}"
                          Example: ["https://drive.google.com/file/d/123", "gs://my_bucket/my_files_dir"]
        tool_context (ToolContext): The tool context

    Returns:
        Dict[str, Any]: Information about the added data and status
    """ 
    # check if corpus exists
    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"Corpus '{corpus_name}' does not exist. Please create it first using the create_corpus tool.",
            "corpus_name": corpus_name,
            "paths": paths,
        }
    # validate inputs
    if not paths or not all(isinstance(path, str) for path in paths):
        return {
            "status": "error",
            "message": "Invalid paths provided. Please provide a list of valid URLs or GCS paths.",
            "corpus_name": corpus_name,
            "paths": paths,
        }
    # pre process paths to validate and convert Google Docs urls to Drive format if needed
    validated_paths = []
    invalid_paths = []
    conversions = []

    for path in paths:
        if not path or not isinstance(path, str):
            invalid_paths.append(f"Path {path} is not a valid string")
            continue
        # Check for Google Docs/Sheets/Slides urls and convert to Drive format if needed
        # examples: https://docs.google.com/document/d/1A2B3C4D5E6F7G8H9I0J
        docs_match = re.match(r"https:\/\/docs\.google\.com\/(?:document|spreadsheets|presentation)\/d\/([a-zA-Z0-9_-]+)(?:\/|$)", path)
        if docs_match:
            # Normalize to standard Drive url format
            file_id = docs_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            conversions.append(f"{path} -> {drive_url}")
            continue
        # check for valid drive url format
        drive_match = re.match(r"https:\/\/drive\.google\.com\/(?:file\/d\/|open\?id=)([a-zA-Z0-9_-]+)(?:\/|$)", path)
        if drive_match:
            # Normalize to the standard drive url format
            file_id = drive_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            if drive_url != path:
                conversions.append(f"{path} -> {drive_url}")
            continue
        #check for GCS paths
        if path.startswith("gs://"):
            validated_paths.append(path)
            continue
        # If we're here, the path wasn't in a recognized format
        invalid_paths.append(f"{path} (Invalid URL format)")

    #if no valid paths, return error
    if not validated_paths:
        return {
            "status":"error",
            "message":"No valid paths provided. Please provide Google Drive URLs or GCS paths.",
            "corpus_name": corpus_name,
            "invalid_paths": invalid_paths
        }
    
    try:
       #get the corpus resource name
       corpus_resource_name = get_corpus_resource_name(corpus_name)
       #setup chunking config
       transformation_config = rag.TransformationConfig(
           chunking_config=rag.ChunkingConfig(
               chunk_size=config["chunk_size"],
               chunk_overlap=config["chunk_overlap"],
           ),
       )
       import_result = rag.import_files(
           corpus_resource_name,
           validated_paths,
           transformation_config=transformation_config,
           max_embedding_requests_per_minute=config["embedding_requests_per_minute"],
       )
       #set this as the current corpus if not already set
       if not tool_context.state.get("current_corpus"):
           tool_context.state["current_corpus"] = corpus_name
       #build the response
       conversion_message = ""
       if conversions:
           conversion_message = " (Converted Google Docs URLs to Drive format)"
       
       return {
           "status": "success",
           "message": f"Successfully added {import_result.imported_rag_files_count} files to corpus '{corpus_name}'{conversion_message}",
           "corpus_name": corpus_name,
           "files_added": import_result.imported_rag_files_count,
           "paths": validated_paths,
           "conversions": conversions,
           "invalid_paths": invalid_paths,
       }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error adding data to corpus '{corpus_name}': {str(e)}",
            "corpus_name": corpus_name,
            "paths": paths,
        }

         
