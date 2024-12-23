import os
import glob
import pickle
import json
import uuid
import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from fastapi import HTTPException
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    CSVLoader,
)
from langchain_openai.embeddings import OpenAIEmbeddings
from domain.doc.document_schema import DocumentMetadata, DocumentCreate
from domain.doc.document_crud import create_document
from sqlalchemy.orm import Session

'''
파일 업로드 후 업로드된 파일을 바탕으로 Retrieve
'''
load_dotenv()

# 벡터 저장소 경로
VECTOR_DB_PATH = "vector_db"
METADATA_PATH = "metadata"
MERGED_DB_PATH = "merged_db"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# 지원하는 파일 타입
SUPPORTED_EXTENSIONS = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".docx": Docx2txtLoader,
    ".csv": CSVLoader,
}


def create_directory_if_not_exists(directory: str):
    """디렉토리가 존재하지 않으면 생성"""
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_document_loader(file_path: str):
    """파일 확장자에 따른 적절한 로더 반환"""
    file_extension = Path(file_path).suffix.lower()
    if file_extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. \
            Supported types: {list(SUPPORTED_EXTENSIONS.keys())}"
        )
    return SUPPORTED_EXTENSIONS[file_extension](file_path)


def process_document(db: Session, file_path: str) -> DocumentMetadata:
    """문서 처리 및 벡터화"""
    # 문서 로드
    loader = get_document_loader(file_path)
    documents = loader.load()

    # 텍스트 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    texts = [doc.page_content for doc in chunks]

    # 임베딩 생성
    embeddings = OpenAIEmbeddings()
    vectors = embeddings.embed_documents(texts)

    # FAISS 인덱스 생성
    dimension = len(vectors[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(vectors, dtype=np.float32))

    # 고유 ID 생성
    unique_id = str(uuid.uuid4())

    # 벡터와 인덱스 저장
    create_directory_if_not_exists(VECTOR_DB_PATH)
    create_directory_if_not_exists(METADATA_PATH)

    embedding_file = f"{VECTOR_DB_PATH}/embeddings_{unique_id}.pkl"
    index_file = f"{VECTOR_DB_PATH}/index_{unique_id}.faiss"

    # 벡터와 메타데이터 저장
    with open(embedding_file, 'wb') as f:
        pickle.dump(vectors, f)

    faiss.write_index(index, index_file)

    # 메타데이터 생성 및 반환
    metadata = DocumentMetadata(
        file_path=file_path,
        chunks=texts,
        embedding_file=embedding_file,
        index_file=index_file
    )

    # 메타데이터 DB 저장
    create_document(
        db, DocumentCreate(
            file_path=file_path,
            embedding_file=embedding_file,
            index_file=index_file,
            unique_id=unique_id
        )
    )

    # 메타데이터 로컬 저장
    with open(f"{METADATA_PATH}/{unique_id}.json", 'w', encoding='utf-8') as f:
        json.dump(metadata.dict(), f, ensure_ascii=False, indent=2)

    # 메타데이터 통합 및 추가
    append_to_merged_index(file_path, MERGED_DB_PATH)

    return metadata


def load_all_metadata() -> List[Dict]:
    """메타데이터 디렉토리에서 모든 메타데이터 파일을 로드"""
    metadata_files = glob.glob(f"{METADATA_PATH}/*.json")
    all_metadata = []

    for metadata_file in metadata_files:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            all_metadata.append(metadata)

    return all_metadata


def merge_faiss_indexes(output_path: str = MERGED_DB_PATH):
    """모든 FAISS 인덱스를 하나로 통합"""
    # 출력 디렉토리 생성
    create_directory_if_not_exists(output_path)

    # 모든 메타데이터 로드
    all_metadata = load_all_metadata()
    if not all_metadata:
        raise HTTPException(
            status_code=404, detail="No indexes found to merge")

    # 모든 임베딩과 청크 텍스트를 저장할 리스트
    all_vectors = []
    all_chunks = []
    source_mapping = []  # 각 벡터의 출처를 추적

    # 각 문서의 임베딩과 청크 수집
    for metadata in all_metadata:
        # 임베딩 로드
        with open(metadata['embedding_file'], 'rb') as f:
            vectors = pickle.load(f)
            all_vectors.extend(vectors)

        # 청크 텍스트 저장
        all_chunks.extend(metadata['chunks'])

        # 소스 매핑 정보 저장
        source_mapping.extend([metadata['file_path']]
                              * len(metadata['chunks']))

    if not all_vectors:
        raise HTTPException(
            status_code=404, detail="No vectors found to merge")

    # NumPy 배열로 변환
    all_vectors = np.array(all_vectors, dtype=np.float32)

    # 새로운 FAISS 인덱스 생성
    dimension = all_vectors.shape[1]
    merged_index = faiss.IndexFlatL2(dimension)
    merged_index.add(all_vectors)

    # 통합된 인덱스 저장
    merged_index_path = f"{output_path}/merged_index.faiss"
    faiss.write_index(merged_index, merged_index_path)

    # 통합된 메타데이터 저장
    merged_metadata = {
        "total_vectors": len(all_vectors),
        "dimension": dimension,
        "source_mapping": source_mapping,
        "chunks": all_chunks,
        "original_files": [metadata['file_path'] for metadata in all_metadata]
    }

    with open(f"{output_path}/merged_metadata.json", 'w',
              encoding='utf-8') as f:
        json.dump(merged_metadata, f, ensure_ascii=False, indent=2)

    return {
        "index_path": merged_index_path,
        "metadata_path": f"{output_path}/merged_metadata.json",
        "total_vectors": len(all_vectors),
        "total_documents": len(all_metadata)
    }


def search_merged_index(query_vector: np.ndarray, k: int = 5,
                        merged_db_path: str = MERGED_DB_PATH):
    """통합된 인덱스에서 검색 수행"""
    # 인덱스 로드
    index_path = f"{merged_db_path}/merged_index.faiss"
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Merged index not found")

    merged_index = faiss.read_index(index_path)

    # 메타데이터 로드
    with open(f"{merged_db_path}/merged_metadata.json", 'r',
              encoding='utf-8') as f:
        metadata = json.load(f)

    # 검색 수행
    distances, indices = merged_index.search(query_vector.reshape(1, -1), k)

    # 결과 구성
    results = []
    for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
        results.append({
            "chunk": metadata["chunks"][idx],
            "source_file": metadata["source_mapping"][idx],
            "distance": float(distance),
            "index": int(idx)
        })

    return results


def append_to_merged_index(file_path: str,
                           merged_db_path: str = MERGED_DB_PATH):
    """새로운 문서를 기존 통합 인덱스에 추가"""
    # 기존 통합 인덱스와 메타데이터 경로
    merged_index_path = f"{merged_db_path}/merged_index.faiss"
    merged_metadata_path = f"{merged_db_path}/merged_metadata.json"

    # 파일 존재 확인
    if not os.path.exists(merged_index_path) or \
            not os.path.exists(merged_metadata_path):
        merge_faiss_indexes(output_path=merged_db_path)

        # raise HTTPException(
        #     status_code=404,
        #     detail="Merged index or metadata not found. "
        #     "Please create merged index first."
        # )

    # 새로운 문서 처리
    try:
        # 문서 로드 및 처리
        loader = get_document_loader(file_path)
        documents = loader.load()

        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        texts = [doc.page_content for doc in chunks]

        # 임베딩 생성
        embeddings = OpenAIEmbeddings()
        new_vectors = embeddings.embed_documents(texts)
        new_vectors = np.array(new_vectors, dtype=np.float32)

        # 기존 인덱스 로드
        merged_index = faiss.read_index(merged_index_path)

        # 기존 메타데이터 로드
        with open(merged_metadata_path, 'r', encoding='utf-8') as f:
            merged_metadata = json.load(f)

        # 차원 일치 확인
        if new_vectors.shape[1] != merged_index.d:
            raise ValueError(
                "New vectors dimension does not match existing index")

        # 백업 생성
        backup_index_path = f"{merged_db_path}/merged_index.faiss.backup"
        backup_metadata_path = f"{merged_db_path}/merged_metadata.json.backup"

        faiss.write_index(merged_index, backup_index_path)
        with open(backup_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(merged_metadata, f, ensure_ascii=False, indent=2)

        try:
            # 새로운 벡터 추가
            merged_index.add(new_vectors)

            # 메타데이터 업데이트
            merged_metadata["total_vectors"] += len(new_vectors)
            merged_metadata["chunks"].extend(texts)
            merged_metadata["source_mapping"].extend([file_path] * len(texts))
            if file_path not in merged_metadata["original_files"]:
                merged_metadata["original_files"].append(file_path)

            # 업데이트된 인덱스와 메타데이터 저장
            faiss.write_index(merged_index, merged_index_path)
            with open(merged_metadata_path, 'w', encoding='utf-8') as f:
                json.dump(merged_metadata, f, ensure_ascii=False, indent=2)

            # 백업 파일 삭제
            os.remove(backup_index_path)
            os.remove(backup_metadata_path)

            return {
                "status": "success",
                "added_vectors": len(new_vectors),
                "total_vectors": merged_metadata["total_vectors"],
                "total_documents": len(merged_metadata["original_files"])
            }

        except Exception as e:
            # 에러 발생 시 백업에서 복구
            if os.path.exists(backup_index_path) and \
                    os.path.exists(backup_metadata_path):
                os.replace(backup_index_path, merged_index_path)
                os.replace(backup_metadata_path, merged_metadata_path)
            raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
