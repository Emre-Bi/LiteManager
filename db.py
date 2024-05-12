import sqlite3
import os

def get_db_connection(db_name):
  """
  
  """ 
  existDBs = os.listdir("./db")
  if db_name == "" or db_name not in existDBs:
    return ""
  connection = sqlite3.connect(f"./db/{db_name}")
  connection.row_factory = sqlite3.Row
  return connection


def get_tables(db_name, page=1):
  """
 
  """
  connection = get_db_connection(db_name)
  offset = (page-1) * 50
  tables = connection.execute(f"SELECT * FROM sqlite_master WHERE type='table' LIMIT 50 OFFSET {offset}").fetchall()
  total_count = connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
  table_names = [row['name'] for row in tables]
  
  return table_names, total_count


def get_columns(table_name, db_name):
  """
  
  """
  connection = get_db_connection(db_name)
  columns = connection.execute(f"SELECT name FROM pragma_table_info('{table_name}');").fetchall()
  column_names = [row['name'] for row in columns]
  return column_names


def get_table_content(table_name, db_name, page=1):
  """
  
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
  connection = get_db_connection(db_name)
  try:  
    connection.execute(f"DROP TABLE {table_name}")
  except Exception as e:
    print(e)

def delete_row(db_name, table_name, row_data):
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
  connection = get_db_connection(db_name)
  columns_str = ", ".join([f"{column} TEXT" for column in columns])
  sql_query = f"CREATE TABLE {table_name} ({columns_str})"
  connection.execute(sql_query)
  connection.commit()
  return 1

if __name__ == '__main__':
  #a = get_tables("test.db")
  #print(a)
  #b = get_columns("employees")
  #print(b)
  c = get_table_content("employees", "test.db")
  print(c)
  
  pass