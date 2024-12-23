from typing import List
from pydantic import BaseModel
import datetime


class DocumentMetadata(BaseModel):
    file_path: str
    chunks: List[str]
    embedding_file: str
    index_file: str


class DocumentCreate(BaseModel):
    file_path: str
    embedding_file: str
    index_file: str
    unique_id: str
    create_date: datetime.datetime | None = None


class Document(BaseModel):
    id: int
    file_path: str
    embedding_file: str
    index_file: str
    unique_id: str
    create_date: datetime.datetime


class DocumentList(BaseModel):
    total: int = 0
    document_list: list[Document] = []
