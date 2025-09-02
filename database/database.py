import psycopg2
from abc import ABC, abstractmethod
from entities.data_class import dbCredentials
from psycopg2.extras import RealDictCursor

class abstractDBConnection(ABC):
    '''Abstract class that defines the interface for opening and closing the database'''

    @abstractmethod
    def opendb(self):
        pass

    @abstractmethod
    def closedb(self):
        pass

class postgreDBConnection(abstractDBConnection):
    #later refactor this class into a context manager
    '''
    PostgreSQL Database connection manager that handles opening and closing the database using
    psycopg2

    Attrtibutes:
        config(dbConfig): A dataclass containing dabase configuration (host, dbname, user, password, cursor_factory)

        conn(psycopg2.extenstion.connection|None): The active database connection. Initialized as None
        and set when opendb() is called.

    Methods:
        opendb():
            Opens a connection to PostgrSQL Database if one is not opened already and returns a connection object
        closedb():
            Closes an active database connection if it exists and resets 'conn' to None
    '''
    def __init__(self, creds: dbCredentials):
        self.creds = creds
        self.conn = None

    def opendb(self):
        if not self.conn:
            self.conn =psycopg2.connect(
                host = self.creds.host,
                dbname= self.creds.dbname,
                user=self.creds.user,
                password = self.creds.password,
                cursor_factory= RealDictCursor
            )
        return self.conn

    def closedb(self):
        if self.conn:
            self.conn.close()
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
            conn.commit()
            return result
        finally:
            cur.close()





### queries go here then inject the queries into the runQuery method

### runQuery executes the SQL statement and closes the cursor pointer

### psql.closedb() will close the db



'''
To open a database, write commands, then execute them, this has to happen:
con = psycopg2.connect() -> connects to the database after logging in
cur = con.cursor() ->allows python code to execute PostgreSQL. It represents a context
                    for executing SQL statements within a connection

cur.execute() -> this is where you pass in SQL statements to be executed
cur.commit() -> this commits any pending transactions the the database
cur.close() ->  this closes the cursor context
con.close() -> closes the database connection



'''