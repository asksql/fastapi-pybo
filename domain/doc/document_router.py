import os
import numpy as np

from fastapi import APIRouter, Depends, HTTPException
from domain.doc.document_tool import (
    process_document,
    search_merged_index,
    SUPPORTED_EXTENSIONS,
    MERGED_DB_PATH
)
from sqlalchemy.orm import Session
from db.postgres import get_db
from langchain_openai.embeddings import OpenAIEmbeddings


router = APIRouter(
    prefix="/api/doc",
)


@router.post("/process-document")
async def process_document_endpoint(file_path: str,
                                    db: Session = Depends(get_db)):
    """
    문서 처리 API 엔드포인트
    """
    try:
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404, detail=f"File not found: {file_path}")

        metadata = process_document(db=db, file_path=file_path)
        return {
            "status": "success",
            "message": "Document processed successfully",
            "metadata": metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-formats")
async def get_supported_formats():
    """지원되는 파일 형식 반환"""
    return {"supported_formats": list(SUPPORTED_EXTENSIONS.keys())}


@router.post("/search-merged")
async def search_merged_endpoint(query: str, k: int = 5,
                                 merged_db_path: str = MERGED_DB_PATH):
    """통합된 인덱스에서 검색하는 엔드포인트"""
    try:
        # 쿼리 텍스트를 벡터로 변환
        embeddings = OpenAIEmbeddings()
        query_vector = np.array(
            embeddings.embed_query(query), dtype=np.float32)

        # 검색 수행
        results = search_merged_index(query_vector, k, merged_db_path)

        return {
            "status": "success",
            "query": query,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
