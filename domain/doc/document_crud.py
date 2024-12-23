from datetime import datetime

from domain.doc.document_schema import DocumentCreate
from models import Document
from sqlalchemy.orm import Session


def get_question_list(db: Session):
    document_list = db.query(Document)
    document_list = document_list.order_by(
        Document.create_date.desc()).distinct().all()
    total = document_list.count()
    return total, document_list


def get_question(db: Session, document_id: int):
    document = db.query(Document).get(document_id)
    return document


def create_document(db: Session, document_create: DocumentCreate):
    db_document = Document(
        file_path=document_create.file_path,
        embedding_file=document_create.embedding_file,
        index_file=document_create.index_file,
        unique_id=document_create.unique_id,
        create_date=datetime.now()
    )
    db.add(db_document)
    db.commit()
