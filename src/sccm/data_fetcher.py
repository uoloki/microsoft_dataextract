import pyodbc
import pandas as pd
from src.common.logger import get_logger

logger = get_logger(__name__)

class SCCMDataFetcher:
    def __init__(self, credentials):
        self.credentials = credentials
        self.connection = self._create_connection()

    def _create_connection_string(self):
        try:
            connection_string = (
                f'DRIVER={self.credentials["driver"]};'
                f'SERVER={self.credentials["server"]};'
                f'DATABASE={self.credentials["database"]};'
                f'UID={self.credentials["username"]};'
                f'PWD={self.credentials["password"]}'
            )
            logger.info("Successfully created connection string")
            return connection_string
        except KeyError as e:
            logger.error(f"Missing key in credentials: {e}")
            raise

    def _create_connection(self):
        try:
            connection_string = self._create_connection_string()
            connection = pyodbc.connect(connection_string)
            logger.info("Successfully connected to the database")
            return connection
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            raise

    def execute_query(self, query):
        """Execute a SQL query and return the results as a DataFrame."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            data = pd.DataFrame.from_records(rows, columns=columns)
            cursor.close()
            logger.info("Successfully executed query and fetched data")
            return data
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise

    def get_hardware_inventory(self):
        query = """
            SELECT
                v_GS_COMPUTER_SYSTEM.Name0 AS ComputerName,
                v_GS_PROCESSOR.Name0 AS ProcessorName,
                v_GS_PROCESSOR.NumberOfCores0 AS NumberOfCores,
                v_GS_X86_PC_MEMORY.TotalPhysicalMemory0 AS TotalPhysicalMemory
            FROM
                v_GS_COMPUTER_SYSTEM
            JOIN
                v_GS_PROCESSOR ON v_GS_COMPUTER_SYSTEM.ResourceID = v_GS_PROCESSOR.ResourceID
            JOIN
                v_GS_X86_PC_MEMORY ON v_GS_COMPUTER_SYSTEM.ResourceID = v_GS_X86_PC_MEMORY.ResourceID
        """
        return self.execute_query(query)

    def get_software_inventory(self):
        query = """
            SELECT
                v_GS_ADD_REMOVE_PROGRAMS.DisplayName0 AS SoftwareName,
                v_GS_ADD_REMOVE_PROGRAMS.Version0 AS Version,
                v_GS_ADD_REMOVE_PROGRAMS.Publisher0 AS Publisher,
                v_GS_COMPUTER_SYSTEM.Name0 AS ComputerName
            FROM
                v_GS_ADD_REMOVE_PROGRAMS
            JOIN
                v_GS_COMPUTER_SYSTEM ON v_GS_ADD_REMOVE_PROGRAMS.ResourceID = v_GS_COMPUTER_SYSTEM.ResourceID
        """
        return self.execute_query(query)

    def get_backup_status(self):
        query = """
            SELECT
                v_GS_BACKUPSTATUS.BackupDateTime0 AS BackupDateTime,
                v_GS_BACKUPSTATUS.BackupStatus0 AS BackupStatus,
                v_GS_COMPUTER_SYSTEM.Name0 AS ComputerName
            FROM
                v_GS_BACKUPSTATUS
            JOIN
                v_GS_COMPUTER_SYSTEM ON v_GS_BACKUPSTATUS.ResourceID = v_GS_COMPUTER_SYSTEM.ResourceID
        """
        return self.execute_query(query)

    def close_connection(self):
        self.connection.close()
        logger.info("Database connection closed")