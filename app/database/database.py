import asyncpg
from dotenv import load_dotenv
import os
import pandas as pd
from abc import ABC, abstractmethod
from app.entities.entities import dbCredentials


load_dotenv()
pool: asyncpg.pool.Pool| None = None 

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
    
    async def execute(self):
        return await self.conn.execute(self.query, *self.params)

async def db_pool():
    global pool
    if pool is None:
        creds = postgreCredentials()
        pool = await asyncpg.create_pool(host=creds.host,
                                 database=creds.dbname,
                                 user=creds.user,
                                 password=creds.password,
                                 min_size=1,
                                 max_size=10)

async def get_db():

    if pool is None:
        await db_pool()
    async with pool.acquire() as conn:
        yield conn


class dataFrameAdapter():

    @staticmethod
    def to_dataframe(data: list[asyncpg.Record]) -> pd.DataFrame:
        return pd.DataFrame([dict(record) for record in data])