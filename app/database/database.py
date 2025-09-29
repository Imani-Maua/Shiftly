import asyncpg
from dotenv import load_dotenv
import os
import pandas as pd
from abc import ABC, abstractmethod
from app.entities.entities import dbCredentials


load_dotenv()


def postgreCredentials():
    credentials = dbCredentials(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    return credentials


class dataRepo(ABC):
    @abstractmethod
    async def getData(self):
        pass

class asyncSQLRepo(dataRepo):

    def __init__(self, conn: asyncpg.Connection, query: str, params: tuple =()):
        self.conn = conn
        self.query = query
        self.params = params
    
    async def getData(self):
        return await self.conn.fetch(self.query, *self.params)

async def get_db():

    creds = postgreCredentials()
    conn = await asyncpg.connect(host=creds.host,
                                 database=creds.dbname,
                                 user=creds.user,
                                 password=creds.password)
    try:
        yield conn
    finally:
        await conn.close()


class dataFrameAdapter():

    @staticmethod
    def to_dataframe(data: list[asyncpg.Record]) -> pd.DataFrame:
        return pd.DataFrame([dict(record) for record in data])