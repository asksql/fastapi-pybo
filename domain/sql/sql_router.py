from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel
from db.oracle import get_db, SQLDatabase4Ora

router = APIRouter(
    prefix="/query",
    tags=["database queries"]
)


class QueryResult(BaseModel):
    result: List[dict]
    query: str


@router.get("/tables")
async def list_tables(db: SQLDatabase4Ora = Depends(get_db)):
    """사용 가능한 테이블 목록 조회"""
    try:
        tables = db.get_usable_table_names()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch tables: {str(e)}"
        )


@router.get("/table/{table_name}")
async def get_table_info(
    table_name: str,
    db: SQLDatabase4Ora = Depends(get_db)
):
    """테이블 정보 조회"""
    try:
        info = db.get_table_info(table_name)
        return {"table_info": info}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch table info: {str(e)}"
        )


@router.get("/execute")
async def execute_query(
    query: str,
    limit: Optional[int] = 10,
    db: SQLDatabase4Ora = Depends(get_db)
):
    """쿼리 실행"""
    try:

        if not query.lower().strip().endswith(
            "fetch first {} rows only".format(limit)
        ):
            query = f"{query} FETCH FIRST {limit} ROWS ONLY"

        result = db._execute(query)
        return QueryResult(result=result, query=query)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(e)}"
        )
