import sqlite3
import pandas as pd
from typing import Any, Iterable

class DatabaseManager:
    def __init__(self, dbPath: str) -> None:
        self.__dbPath = dbPath
        self.__connection: sqlite3.Connection | None = None
        
    def Connect(self):
        if not self.__connection:
            self.__connection = sqlite3.connect(self.__dbPath)
    
    def Close(self):
        if self.__connection:
            self.__connection.close() #type: ignore
    
    def Exec(self, sql: str, params: Iterable[Any] = ()):
        if self.__connection is None:
            self.Connect()

        cursor = self.__connection.cursor() #type: ignore
        cursor.execute(sql, tuple(params))
        self.__connection.commit() #type: ignore
        return cursor

    def FetchOne(self, sqlQuery: str, params: Iterable[Any] = ()):
        if self.__connection is None:
            self.Connect()
        cursor = self.__connection.cursor() #type: ignore
        cursor.execute(sqlQuery, tuple(params))
        self.__connection.commit() #type: ignore
        row = cursor.fetchone()
        self.Close()
        return row

    def FetchAll(self, sqlQuery: str, params: Iterable[Any] = ()):
        if self.__connection is None:
            self.Connect()
        df = pd.read_sql_query(sqlQuery, self.__connection)
        self.Close()
        return df
