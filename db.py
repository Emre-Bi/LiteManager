import sqlite3
import os

def get_db_connection(db_name):
  """
  Establishes a connection to the specified SQLite database.

    Parameters:
        db_name (str): The name of the SQLite database file.

    Returns:
        connection: A connection object to the SQLite database, or an empty string if the database does not exist.
  """ 
  existDBs = os.listdir("./db")
  if db_name == "" or db_name not in existDBs:
    return ""
  connection = sqlite3.connect(f"./db/{db_name}")
  connection.row_factory = sqlite3.Row
  return connection


def get_tables(db_name, page=1):
  """
   Retrieves a list of table names from the specified SQLite database.

    Parameters:
        db_name (str): The name of the SQLite database file.
        page (int, optional): The page number for pagination. Default is 1.

    Returns:
        tuple: A tuple containing:
            - list: A list of table names.
            - int: Total count of tables in the database.
  """
  connection = get_db_connection(db_name)
  offset = (page-1) * 50
  tables = connection.execute(f"SELECT * FROM sqlite_master WHERE type='table' LIMIT 50 OFFSET {offset}").fetchall()
  total_count = connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
  table_names = [row['name'] for row in tables]
  
  return table_names, total_count


def get_columns(table_name, db_name):
  """
  Retrieves a list of column names for the specified table in the SQLite database.

    Parameters:
        table_name (str): The name of the table.
        db_name (str): The name of the SQLite database file.

    Returns:
        list: A list of column names.
  """
  connection = get_db_connection(db_name)
  columns = connection.execute(f"SELECT name FROM pragma_table_info('{table_name}');").fetchall()
  column_names = [row['name'] for row in columns]
  return column_names


def get_table_content(table_name, db_name, page=1):
  """
  Retrieves content of a table from the specified SQLite database.

    Parameters:
        table_name (str): The name of the table.
        db_name (str): The name of the SQLite database file.
        page (int, optional): The page number for pagination. Default is 1.

    Returns:
        tuple: A tuple containing:
            - list: A list of dictionaries representing rows of the table.
            - int: Total count of rows in the table.
            - list: A list of column names.
  """
  connection = get_db_connection(db_name)
  columns = get_columns(table_name, db_name)
  offset = (page-1) * 50
  rows = connection.execute(f"SELECT * FROM {table_name} LIMIT 50 OFFSET {offset}").fetchall()
  total_count = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
  all_rows = []

  for row in rows:
    row_data = {}
    for column in columns:
      row_data[column] = row[column]
    all_rows.append(row_data)
  return all_rows, total_count, columns


def delete_table(db_name, table_name):
  """
  Deletes a table from the specified SQLite database.

    Parameters:
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table to delete.
  """
  connection = get_db_connection(db_name)
  try:  
    connection.execute(f"DROP TABLE {table_name}")
  except Exception as e:
    print(e)

def delete_row(db_name, table_name, row_data):
  """
  Deletes a row from the specified table in the SQLite database based on the provided row data.

    Parameters:
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table from which to delete the row.
        row_data (dict): A dictionary containing column-value pairs for the row to be deleted.

    Returns:
        int: Returns 1 if the row was successfully deleted, otherwise returns 0.
  """
  connection = get_db_connection(db_name=db_name)
  columns = get_columns(db_name=db_name, table_name=table_name)
  cursor = connection.cursor()
  if not all(column in row_data.keys() for column in columns):
    return 0

  column_value_pairs = [f"{column} = ?" for column in row_data.keys()]
  where_clause = ' AND '.join(column_value_pairs)
  values = list(row_data.values())
  sql_query = f"DELETE FROM {table_name} WHERE {where_clause};"
  cursor.execute(sql_query, values)
  connection.commit() 
  return 1

def add_row(db_name, table_name, row_data):
  """
  Inserts a new row into the specified table in the SQLite database with the provided row data.

    Parameters:
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table to which the row will be added.
        row_data (dict): A dictionary containing column-value pairs for the new row.

    Returns:
        int: Returns 1 if the row was successfully added, otherwise returns 0.
  """
  connection = get_db_connection(db_name=db_name)
  columns = get_columns(db_name=db_name, table_name=table_name)
  cursor = connection.cursor()
  if not all(column in row_data.keys() for column in columns):
      return 0
  columns = ', '.join(row_data.keys())
  placeholders = ', '.join(['?' for _ in range(len(row_data))])
  sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
  try:
      cursor.execute(sql_query, list(row_data.values()))
      connection.commit()
      return 1
  except Exception as e:
      print(f"Error: {e}")
      connection.rollback()
      return 0

def add_table(db_name, table_name, columns):
  """
  Creates a new table in the specified SQLite database with the provided name and columns.

    Parameters:
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table to create.
        columns (list): A list of column names for the new table.

    Returns:
        int: Returns 1 if the table was successfully created, otherwise returns 0.
  """
  connection = get_db_connection(db_name)
  columns_str = ", ".join([f"{column} TEXT" for column in columns])
  sql_query = f"CREATE TABLE {table_name} ({columns_str})"
  connection.execute(sql_query)
  connection.commit()
  return 1
