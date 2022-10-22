import sqlite3
import time
from os import path, getcwd, chmod
from typing import Union
from utils.queue.job import Job

class Store:
    __DB_FILE_PATH = '%s/data/store.db'

    __CREATE_QUEUE_TABLE_SQL = '''
        CREATE TABLE queue (
            id                     text,
            type                   integer,
            additional_values_json text,
            status                 integer,
            error_message          text,
            created_at             integer,
            updated_at             integer,

            UNIQUE (id) ON CONFLICT FAIL
        );
    '''

    __CREATE_USERS_TABLE_SQL = '''
        CREATE TABLE users (
            id         integer,
            name       text,
            type       integer,
            status     integer,
            credits    integer,
            created_at integer,
            updated_at integer,

            UNIQUE (id) ON CONFLICT FAIL
        );
    '''

    __INSERT_JOB_SQL = '''
        INSERT INTO queue
        VALUES (:id, :type, :additional_values_json, :status, :error_message, :created_at, :updated_at);
    '''

    __INSERT_USER_SQL = '''
        INSERT INTO users
        VALUES (:id, :name, :type, :status, :credits, :created_at, :updated_at);
    '''

    __SELECT_JOB_BY_STATUS_SQL = '''
        SELECT
            id,
            type,
            additional_values_json,
            status,
            error_message,
            created_at,
            updated_at
        FROM queue
        WHERE status = :status
        ORDER BY created_at ASC, updated_at ASC
        LIMIT 1;
    '''

    __SELECT_JOB_BY_CREATED_AT_SQL = '''
        SELECT
            id,
            type,
            additional_values_json,
            status,
            error_message,
            created_at,
            updated_at
        FROM queue
        WHERE created_at < :created_at
        ORDER BY created_at ASC, updated_at ASC
        LIMIT 1;
    '''

    __SELECT_JOBS_COUNT_SQL = '''
        SELECT
            COUNT(id) AS "count",
            status
        FROM queue
        GROUP BY status;
    '''

    __SELECT_USER_BY_ID_SQL = '''
        SELECT
            id,
            name,
            type,
            status,
            credits,
            created_at,
            updated_at
        FROM users
        WHERE id = :id
        LIMIT 1;
    '''

    __UPDATE_JOB_BY_ID_SQL = '''
        UPDATE queue
        SET
            status = :status,
            error_message = :error_message,
            updated_at = :updated_at
        WHERE id = :id; 
    '''

    __UPDATE_USER_BY_ID_SQL = '''
        UPDATE users
        SET
            status = :status,
            credits = :credits,
            updated_at = :updated_at
        WHERE id = :id; 
    '''

    __DELETE_JOB_BY_ID_SQL = '''
        DELETE FROM queue
        WHERE id = :id;
    '''

    __DELETE_JOB_BY_STATUS_SQL = '''
        DELETE FROM queue
        WHERE status = :status;
    '''

    __dbConnection = None

    def __init__(self):
        dbFilePath = self.__getDatabaseFilePath()

        if not path.exists(dbFilePath) or not path.isfile(dbFilePath):
            self.__initStore()
            chmod(dbFilePath, 0o755)

    def insertJob(
        self,
        id:                   str,
        type:                 int,
        additionalValuesJson: str,
        status:               int,
        errorMessage:         Union[str, None]
    ) -> bool:
        params = {
            'id':                     id,
            'type':                   type,
            'additional_values_json': additionalValuesJson,
            'status':                 status,
            'error_message':          str(errorMessage),
            'created_at':             int(time.time()),
            'updated_at':             0
        }

        self.__executeSql(self.__INSERT_JOB_SQL, params)

        return True

    def insertUser(
        self,
        id:      int,
        name:    str,
        type:    int,
        status:  int,
        credits: int
    ) -> bool:
        params = {
            'id':         id,
            'name':       name,
            'type':       type,
            'status':     status,
            'credits':    credits,
            'created_at': int(time.time()),
            'updated_at': 0
        }

        self.__executeSql(self.__INSERT_USER_SQL, params)

        return True

    def getJobByStatus(self, status: int) -> Union[dict, None]:
        params = {
            'status': status
        }

        return self.__getQueueRow(self.__SELECT_JOB_BY_STATUS_SQL, params)

    def getJobByCreatedAt(self, createdAt: int) -> Union[dict, None]:
        params = {
            'created_at': createdAt
        }

        return self.__getQueueRow(self.__SELECT_JOB_BY_CREATED_AT_SQL, params)

    def getJobsCount(self) -> dict:
        jobsCount = {
            'all': 0
        }

        sqliteRows = self.__getRows(self.__SELECT_JOBS_COUNT_SQL)

        for sqliteRow in sqliteRows:
            jobsCount[Job.getStatusTitle(sqliteRow['status'])] = int(sqliteRow['count'])
            jobsCount['all'] = jobsCount['all'] + int(sqliteRow['count'])

        return jobsCount

    def getUserById(self, id: int) -> Union[dict, None]:
        params = {
            'id': id
        }

        return self.__getUserRow(self.__SELECT_USER_BY_ID_SQL, params)

    def updateJob(
        self,
        id:           str,
        status:       int,
        errorMessage: Union[str, None] = None
    ) -> bool:
        params = {
            'id':            id,
            'status':        status,
            'error_message': str(errorMessage),
            'updated_at':    int(time.time())
        }

        self.__executeSql(self.__UPDATE_JOB_BY_ID_SQL, params)

        return True

    def updateUser(
        self,
        id:      int,
        status:  int,
        credits: int
    ) -> bool:
        params = {
            'id':         id,
            'status':     status,
            'credits':    credits,
            'updated_at': int(time.time())
        }

        self.__executeSql(self.__UPDATE_USER_BY_ID_SQL, params)

        return True

    def removeJobById(self, id: str) -> bool:
        params = {
            'id': id
        }

        self.__executeSql(self.__DELETE_JOB_BY_ID_SQL, params)

        return True

    def removeJobByStatus(self, status: int) -> bool:
        params = {
            'status': status
        }

        self.__executeSql(self.__DELETE_JOB_BY_STATUS_SQL, params)

        return True

    def close(self) -> None:
        if self.__dbConnection is not None:
            self.__dbConnection.close()
            self.__dbConnection = None

    def __connect(self) -> None:
        dbFilePath = self.__getDatabaseFilePath()

        self.__dbConnection = sqlite3.connect(dbFilePath)
        self.__dbConnection.row_factory = sqlite3.Row

    def __getDatabaseFilePath(self) -> str:
        return self.__DB_FILE_PATH % getcwd()

    def __initStore(self) -> str:
        self.__executeSql(self.__CREATE_QUEUE_TABLE_SQL)
        self.__executeSql(self.__CREATE_USERS_TABLE_SQL)

    def __executeSql(self, sql: str, params: Union[dict, None] = None) -> None:
        if self.__dbConnection is None:
            self.__connect()

        cursor = self.__dbConnection.cursor()

        if params != None:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        self.__dbConnection.commit()

    def __getRow(self, sql: str, params: Union[dict, None] = None) -> Union[sqlite3.Row, None]:
        if self.__dbConnection is None:
            self.__connect()

        cursor = self.__dbConnection.cursor()

        if params != None:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        self.__dbConnection.commit()

        return cursor.fetchone()

    def __getRows(self, sql: str, params: Union[dict, None] = None) -> list:
        if self.__dbConnection is None:
            self.__connect()

        cursor = self.__dbConnection.cursor()

        if params != None:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        self.__dbConnection.commit()

        return cursor.fetchall()

    def __getQueueRow(self, sql: str, params: Union[dict, None] = None) -> Union[dict, None]:
        sqliteRow = self.__getRow(sql, params)

        if sqliteRow == None:
            return None

        return {
            'id':                     sqliteRow['id'],
            'type':                   sqliteRow['type'],
            'additional_values_json': sqliteRow['additional_values_json'],
            'status':                 sqliteRow['status'],
            'error_message':          sqliteRow['error_message'],
            'created_at':             sqliteRow['created_at'],
            'updated_at':             sqliteRow['updated_at']
        }

    def __getUserRow(self, sql: str, params: Union[dict, None] = None) -> Union[dict, None]:
        sqliteRow = self.__getRow(sql, params)

        if sqliteRow == None:
            return None

        return {
            'id':         sqliteRow['id'],
            'name':       sqliteRow['name'],
            'type':       sqliteRow['type'],
            'status':     sqliteRow['status'],
            'credits':    sqliteRow['credits'],
            'created_at': sqliteRow['created_at'],
            'updated_at': sqliteRow['updated_at']
        }
