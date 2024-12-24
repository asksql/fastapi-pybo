from langchain_community.utilities import SQLDatabase
from fastapi import Depends
from typing import Annotated
import cx_Oracle
from settings import get_settings


def get_db() -> SQLDatabase:
    """데이터베이스 인스턴스를 반환하는 의존성 함수"""
    settings = get_settings()
    connection_string = f"oracle+cx_oracle:\
//{settings.DB_USER}:{settings.DB_PASSWORD}@\
{settings.DB_HOST}:{settings.DB_PORT}/\
?service_name={settings.DB_SERVICE}"

    try:
        cx_Oracle.init_oracle_client(lib_dir=settings.ORACLE_CLIENT_DIR)
    except Exception as e:
        print(e)

    return SQLDatabase4Ora.from_uri(
        connection_string
    )


class SQLDatabase4Ora(SQLDatabase):
    # 오라클 cx_oracle과의 호환성 문제로 인한 get_table_info메소디 오버라이딩
    def get_table_info(self, table_names=None):
        if isinstance(table_names, str):
            query = f"""SELECT
                dbms_metadata.get_ddl('TABLE', '{table_names.upper()}')
                FROM DUAL"""
            return super().run(query)
        else:
            ddl_list = []
            for table_name in table_names:
                query = f"""SELECT
                    dbms_metadata.get_ddl('TABLE', '{table_name.upper()}')
                    FROM DUAL"""
                ddl_list.append(super().run(query))
            return ddl_list


# 의존성 타입 정의 (옵션)
DB = Annotated[SQLDatabase4Ora, Depends(get_db)]
