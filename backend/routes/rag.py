from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from database.vector_db import vector_db

router = APIRouter()

class RAGQueryRequest(BaseModel):
    query: str

class RAGQueryResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
    engine: str

@router.post("/query", response_model=RAGQueryResponse)
def query_academic_policies(request: RAGQueryRequest):
    """
    Graph-RAG Endpoint: Queries the vector database for academic policies matching the request.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty")
        
    match = vector_db.query_policy(request.query)
    
    engine = "chromadb_semantic_search" if not vector_db.is_mock else "fallback_keyword_search"
    
    if not match:
        return RAGQueryResponse(
            status="NO_DATA_FOUND",
            result=None,
            engine=engine
        )
        
    return RAGQueryResponse(
        status="SUCCESS",
        result=match,
        engine=engine
    )
