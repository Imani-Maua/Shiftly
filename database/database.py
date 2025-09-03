import psycopg2
from abc import ABC, abstractmethod
from app.entities.entities import dbCredentials
from psycopg2.extras import RealDictCursor
import pandas as pd

class abstractDBContextManager(ABC):
    '''Abstract class that defines the interface for opening and closing the database'''

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass



def postgreCredentials():
        credentials = dbCredentials(
    host= "localhost",
    dbname= "*******",
    user= "******",
    password= "******",
    cursor_factory= RealDictCursor
)
        return credentials


class postgreContextManager(abstractDBContextManager):
    def __init__(self, creds: dbCredentials):
        self.creds = creds
        self.conn = None

    def __enter__(self):
        if not self.conn:
            self.conn = psycopg2.connect(host = self.creds.host,
                dbname= self.creds.dbname,
                user=self.creds.user,
                password = self.creds.password,
                cursor_factory= RealDictCursor)
        return self.conn
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        try:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
        finally:
            try:
                self.conn.close()
            except Exception as close_exc:
                print(f'Warning: Error closing connection {close_exc}')
            self.conn = None

        

class executeQuery:
    '''
    SQL Query Manager for executing SQL Queries on an active database connection
    This class provides a static method to execute SQL Queries with optional parameters and fetch results if needed.
    It handles cursor management and ensures that the connection is committed after execution.
    '''

    @staticmethod
    def runQuery(conn, query, params=None, fetch=False):
        '''
        Executes an SQL query on the given database connection

        Args:
            conn: A connection object to the database
            query: An SQL Query that is to be executed
            fetch: A boolean which tells the method whether to fetch results or not.

        Return:
            list of tuples or dicts: If fetch is true, it return a list of tuples or dicts.
        '''

        cur = conn.cursor()
        try:
            cur.execute(query, params or ())
            result = cur.fetchall() if fetch else None
            return result
        finally:
            cur.close()


class generateDataRepo:

    def __init__(self, query: str, conn: postgreContextManager):
        self.query = query
        self.conn = conn
    
    def retrieveData(self):
        with self.conn as manager:
            return executeQuery.runQuery(manager, self.query, fetch=True)


class dbDataRepo(ABC):

    @abstractmethod
    def getData(self):
        pass


class dataFrameAdapter:
     '''
     Adapter class that transform raw data into a Pandas DataFrame.

     This class serves as a transformation layer between the repository which generates
     raw data, and the rest of the application which operates on a DataFrame
     '''
     @staticmethod
     def to_dataframe(data:list) -> pd.DataFrame:
        '''
        Converts a list of talent records into a Pandas DataFrame

        Args:
            talents(list): A list of talent records where each record is a dictionary

        Return:
            talents(pd.DataFrame): A Pandas dataframe which is suitable for manipulation such as
                                    filtering, grouping, and analysis.
        '''
        return pd.DataFrame(data)
