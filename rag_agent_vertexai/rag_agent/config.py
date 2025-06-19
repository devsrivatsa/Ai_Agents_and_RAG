from pydantic import BaseModel, Field


class Config(BaseModel):
    rag_agent_model: str = Field(
        description="The model to use for the RAG agent",
        default="gemini-2.5-flash"
    )
    text_embedding_model: str = Field(
        description="The model used for text embedding",
        default="publishers/google/models/text-embedding-005"
    )
    rag_query_model: str = Field(
        description="The model used for RAG queries",
        default="gemini-2.5-flash"
    )
    chunk_size: int = Field(
        description="The size of chunks for processing",
        default=512
    )
    chunk_overlap: int = Field(
        description="The overlap size between chunks",
        default=100
    )
    top_k: int = Field(
        description="The number of top results to return",
        default=3
    )
    distance_threshold: float = Field(
        description="The threshold for distance in embeddings",
        default=0.5
    )
    embedding_requests_per_minute: int = Field(
        description="The maximum number of embedding requests per minute",
        default=1000
    )
    project_id: str = Field(
        description="Google Cloud Project ID",
        default=""
    )
    location: str = Field(
        description="Google Cloud location/region",
        default="us-central1"
    )

    def config_dict(self):
        return self.model_dump()

if __name__ == "__main__":
    config = Config().config_dict()
    print(config)   