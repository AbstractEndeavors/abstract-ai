import os
from abstract_pandas import *
from sqlalchemy import Boolean, create_engine, String, BigInteger, JSON, Text, cast, Index, MetaData, Table, text, inspect, Column, Integer, Float
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, declarative_base
from abstract_utilities import *

def get_all_key_values(data, parent_key='', sep='_'):
    items = {}
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.update(get_all_key_values(value, new_key, sep=sep))
        else:
            items[new_key] = value
    return items

def get_file_parts(path):
    dirName = os.path.dirname(path)
    baseName = os.path.basename(path)
    fileName, ext = os.path.splitext(baseName)
    return {"dirName": dirName, "baseName": baseName, "fileName": fileName, "ext": ext}

def get_db_url(dbPath):
    dbUrl = f"sqlite:///{dbPath}"
    return dbUrl

def get_db_engine(dbUrl=None, dbPath=None):
    if dbUrl is None:
        if dbPath is None:
            return
        dbUrl = get_db_url(dbPath)
    return create_engine(dbUrl)

def get_user_input(text,default='y'):
    choices = '(y/n)' if default in ['y','n'] else ''
 or default
    if choices:
        response = response.lower() == 'y'
    return response
    
def enter_value_text(typ="", action="to filter by", parentObject="selection"):
    return input(f"Enter {typ} value {action} in {parentObject}: ")

def get_type_change_list():
    return ["String", "Integer", "Float", "JSON"]

def capitalize(string):
    return f"{string[0].upper()}{string[1:].lower()}"

def pluralize(string):
    return f"{eatOuter(string, ['s'])}s"

def get_integer_input(prompt, min_value, max_value):
    while True:
        try:
            value = int(input(f"{prompt} ({min_value}-{max_value}): "))
            if min_value <= value <= max_value:
                return value
            else:
                print(f"Please enter a number between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def enumerate_selections(obj_list=[], parentObject="column", childObject=None):
    parent_plural = pluralize(capitalize(parentObject))
    output = f"Available {parent_plural}:" if childObject is None else f"{parent_plural} in {childObject}:"
    for idx, value in enumerate(obj_list):
        print(f"{idx + 1}. {value}")
    return obj_list

def list_objects(obj_list=None, parentObject=None, object_type='column'):
    if not obj_list:
        print(f"No {pluralize(object_type)} available.")
        return None
    object_choice = get_integer_input(f"Choose a {object_type}", 1, len(obj_list)) - 1
    return obj_list[object_choice]

def get_field_choice(obj_list, parentObject=None, object_type=None):
    enumerate_selections(obj_list=obj_list, parentObject=parentObject)
    return list_objects(obj_list=obj_list, parentObject=None, object_type=object_type)

class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def get_db_name(dbName=None, dbPath=None, dbUrl=None):
    if dbName:
        return dbName
    fileParts_js = get_file_parts(dbPath or dbUrl)
    return fileParts_js.get("fileName")


def create_class_from_dict(class_name, class_dict, base):
    attributes = {
        '__tablename__': class_name.lower(),
        'id': Column(Integer, primary_key=True, autoincrement=True)
    }

    unique_keys = class_dict.get('unique_keys', [])

    def handle_nested(col_name, col_type):
        if isinstance(col_type, dict):
            return Column(JSON)
        elif isinstance(col_type, list):
            return Column(JSON)
        else:
            raise ValueError(f"Unsupported column type: {col_type}")

    for col_name, col_type in class_dict['valueKeys'].items():
        if col_type == "TEXT":
            col = Column(String)
        elif col_type == "INTEGER":
            col = Column(Integer)
        elif col_type == "FLOAT" or col_type == "REAL":
            col = Column(Float)
        elif col_type == "JSON" or col_type == "ARRAY":
            col = Column(JSON)
        elif col_type == "BOOL":
            col = Column(Boolean)
        elif isinstance(col_type, dict) or isinstance(col_type, list):
            col = handle_nested(col_name, col_type)
        else:
            raise ValueError(f"Unsupported column type: {col_type}")

        attributes[col_name] = col

        if col_name in unique_keys:
            attributes[f'ix_{col_name}'] = Index(f'ix_{class_name.lower()}_{col_name}', col, unique=True)

    return type(class_name, (base,), attributes)
def flatten_json(data, parent_key='', sep='_'):
    """
    Flatten a JSON object into a single dictionary with keys indicating the nested structure.

    Args:
        data (dict): The JSON object to flatten.
        parent_key (str): The base key to use for nested keys (used in recursive calls).
        sep (str): The separator to use between keys.

    Returns:
        dict: The flattened JSON object.
    """
    items = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                items.extend(flatten_json(value, new_key, sep=sep).items())
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    items.extend(flatten_json(item, f"{new_key}{sep}{i}", sep=sep).items())
            else:
                items.append((new_key, value))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            items.extend(flatten_json(item, f"{parent_key}{sep}{i}", sep=sep).items())
    else:
        items.append((parent_key, data))

    return dict(items)
# Generic function to check if a record exists
def record_exists(session, model, **kwargs):
    query = session.query(model)
    for key, value in kwargs.items():
        query = query.filter(getattr(model, key) == value)
    return query.first() is not None

class sessionManager(metaclass=SingletonMeta):
    def __init__(self, Base=None,db_vars=None,dbDir=None):
        self.dbTracker = {}
        self.Base = Base or declarative_base()
        self.db_vars=db_vars or {}
        self.dbDir=dbDir or os.path.join(os.getcwd(),"databases")
        self.initialize_all_dbs()
    def initialize_all_dbs(self):
        for dbName, db_info in self.db_vars.items():
            dbPath = os.path.join(self.dbDir,f"{dbName}.db")
            dbName = get_db_name(dbPath=dbPath, dbUrl=get_db_url(dbPath))
            self.initialize_db(dbName=dbName,dbPath=dbPath, db_tables=db_info)
    def initialize_db(self,dbName=None, dbPath=None, dbUrl=None, db_tables=None):
        dbUrl = dbUrl or get_db_url(dbPath)
        
        self.checkDatabaseName(dbName=dbName, dbPath=dbPath, dbUrl=dbUrl, db_tables=self.db_vars[dbName])
        self.create_session(dbPath=dbPath, dbUrl=dbUrl)
        self.create_tables(dbName)
        return dbName

    def get_dbName(self, dbName=None, dbPath=None, dbUrl=None):
        if dbName is None and dbUrl is None and dbPath is None:
            return dbName
        elif dbName is None and (dbUrl is not None or dbPath is not None):
            dbName = get_db_name(dbPath=dbPath, dbUrl=dbUrl)
        return dbName

    def create_session(self, dbPath=None, dbUrl=None):
        dbName = get_db_name(dbPath=dbPath, dbUrl=dbUrl)
        self.dbTracker[dbName]["engine"] = get_db_engine(dbUrl=dbUrl, dbPath=dbPath)
        self.Base.metadata.bind = self.dbTracker[dbName]["engine"]
        self.solcatcherDBSession = sessionmaker(bind=self.dbTracker[dbName]["engine"])
        self.dbTracker[dbName]["session"] = self.solcatcherDBSession()

    def create_tables(self, dbName=None, dbPath=None, dbUrl=None):
        self.Base.metadata.create_all(self.dbTracker[dbName]["engine"])
        dbName = get_db_name(dbName=dbName, dbPath=dbPath, dbUrl=dbUrl)
        for table, columns_info in self.dbTracker[dbName]["db_tables"].items():
            columns = list(columns_info["valueKeys"].keys())
            columns_defs = self.flatten_columns_defs(columns_info["valueKeys"])
            create_table_sql = text(f'CREATE TABLE IF NOT EXISTS "{table}" ({columns_defs});')
            self.dbTracker[dbName]["session"].execute(create_table_sql)
        self.dbTracker[dbName]["session"].commit()


    def flatten_columns_defs(self, valueKeys):
        column_defs = []
        for col, dtype in valueKeys.items():
            col_name = f'"{col}"'
            if isinstance(dtype, dict):
                column_defs.append(f"{col_name} JSON")
            elif isinstance(dtype, list):
                column_defs.append(f"{col_name} JSON")
            else:
                column_defs.append(f"{col_name} {dtype}")
        return ", ".join(column_defs)

    def checkDatabaseName(self, dbName=None, dbPath=None, dbUrl=None, dbBrowser=None, db_tables=None, primary_types=None):
        dbName = self.get_dbName(dbName=dbName, dbPath=dbPath, dbUrl=dbUrl)
        if dbName not in self.dbTracker:
            self.dbTracker[dbName] = {"dbUrl": dbUrl, "dbPath": dbPath, "db_tables": db_tables, "columns_info": self.db_vars.get(dbName),"classes":{}}
            for key,value in self.db_vars.get(dbName).items():
                self.dbTracker[dbName]["classes"][key] = create_class_from_dict(capitalize(key), value,self.Base)
                
    def close_session(self, dbName=None, dbPath=None, dbUrl=None):
        dbName = self.get_dbName(dbName=dbName, dbPath=dbPath, dbUrl=dbUrl)
        self.dbTracker[dbName]["session"].close()

    # Function to insert a record
    def insert_record(self, dbName, class_name, record, unique_keys=None):
        model = self.dbTracker[dbName]["classes"][class_name]
        session = self.dbTracker[dbName]["session"]
        unique_keys=make_list(unique_keys or self.dbTracker[dbName]["columns_info"][class_name]['unique_keys'])
        if record_exists(session, model, **{key: record[key] for key in unique_keys}):
            #print(f"Duplicate entry found with keys: {unique_keys}. Skipping...")
            return
        new_record = model(**record)
        try:
            session.add(new_record)
            session.commit()
        except IntegrityError:
            session.rollback()
            print(f"Integrity error for record: {record}. Rolling back transaction.")


    # Function to update a record
    def update_record(self, dbName, table_name, record, conditions):
        session = self.dbTracker[dbName]["session"]
        set_clause = ", ".join([f'"{key}" = :{key}' for key in record.keys()])
        condition_clause = " AND ".join([f'"{key}" = :{key}' for key in conditions.keys()])
        update_sql = text(f'UPDATE "{table_name}" SET {set_clause} WHERE {condition_clause}')
        session.execute(update_sql, {**record, **conditions})
        session.commit()

    # Function to delete a record
    def delete_record(self, dbName, table_name, conditions):
        session = self.dbTracker[dbName]["session"]
        condition_clause = " AND ".join([f'"{key}" = :{key}' for key in conditions.keys()])
        delete_sql = text(f'DELETE FROM "{table_name}" WHERE {condition_clause}')
        session.execute(delete_sql, conditions)
        session.commit()
class DatabaseBrowser:
    def __init__(self, dbUrl=None, dbPath=None):
        self.dbUrl = dbUrl or get_db_url(dbPath)
        self.engine = create_engine(self.dbUrl)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.metadata = MetaData()
        self.inspector = inspect(self.engine)
    def list_tables(self):
        tables = self.inspector.get_table_names()
        return enumerate_selections(obj_list=tables,parentObject="table",childObject=None)

    def table_list(self):
        obj_list = self.list_tables()
        return list_objects(obj_list=obj_list,object_type='table')
    def list_columns(self, table_name):
        try:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            columns = [column.name for column in table.columns]
            return enumerate_selections(obj_list=columns,parentObject="column",childObject=table)
        except Exception as e:
            print(f"Error loading table {table_name}: {e}")
            return []

    def column_list(self, table_name=None):
        if table_name is None:
            table_name = self.table_list()
        if table_name is None:
            print("No table selected.")
            return None
        obj_list = self.list_columns(table_name)  
        return list_objects(obj_list=obj_list,parentObject=table_name,object_type='column')
    def view_table(self, table_name, start=0, end=5):
        try:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            query = table.select().offset(start).limit(end - start)
            result = self.session.execute(query)
            rows = result.fetchall()

            if rows:
                df = pd.DataFrame(rows)
                df.columns = result.keys()
                pd.set_option('display.max_rows', None)
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', None)
                pd.set_option('display.max_colwidth', None)
                print(df)
                pd.reset_option('display.max_rows')
                pd.reset_option('display.max_columns')
                pd.reset_option('display.width')
                pd.reset_option('display.max_colwidth')
            else:
                print(f"No data found in table {table_name} from row {start} to {end}")
        except Exception as e:
            print(f"Error viewing table {table_name}: {e}")
    def alter_column_type(self, table_name, column_name, new_type):
        """Alter the type of a specific column in a table."""
        if new_type not in ['String', 'Integer', 'Float']:
            print("Invalid type. Please choose from 'String', 'Integer', or 'Float'.")
            return
        
        try:
            # Load the table
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            old_column = table.c[column_name]
            
            # Determine the new column type
            if new_type == 'String':
                new_column = Column(column_name, String, nullable=old_column.nullable)
            elif new_type == 'Integer':
                new_column = Column(column_name, Integer, nullable=old_column.nullable)
            elif new_type == 'Float':
                new_column = Column(column_name, Float, nullable=old_column.nullable)
            
            # Perform the column type change
            with self.engine.connect() as connection:
                connection.execute(text(f"ALTER TABLE {table_name} RENAME COLUMN {column_name} TO {column_name}_old"))
                connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {new_type}"))
                connection.execute(text(f"UPDATE {table_name} SET {column_name} = {column_name}_old"))
                connection.execute(text(f"ALTER TABLE {table_name} DROP COLUMN {column_name}_old"))
                connection.commit()
            
            print(f"Column {column_name} in table {table_name} successfully altered to {new_type}.")
        except Exception as e:
            print(f"Error altering column type: {e}")

    def update_all_entries(self, table_name, column_name, new_value):
        """Update all entries in a specific column with a new value."""
        try:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            query = table.update().values({column_name: new_value})
            result = self.session.execute(query)
            self.session.commit()
            print(f"All entries in column {column_name} of table {table_name} updated to {new_value}.")
        except Exception as e:
            print(f"Error updating entries: {e}")

    def export_data_by_key_value(self, table_name,value, file_path,key='zipcode' ):
        """Export data from a specific zipcode to an Excel file."""
        try:
            query = text(f"SELECT * FROM {table_name} WHERE {key} = :{key}")
            result = self.session.execute(query, {f"{key}": value})
            rows = result.fetchall()

            if rows:
                df = pd.DataFrame(rows)
                df.columns = result.keys()
                df.to_excel(file_path, index=False)
                print(f"Data for {key} {value} exported to {file_path}")
            else:
                print(f"No data found for {key} {value} in table {table_name}")
        except Exception as e:
            print(f"Error exporting data: {e}")
    
    def search_table(self, table_name, column_name, search_value, print_value=False):
        """
        Search a table for specific values in a column.

        Args:
            table_name (str): The name of the table to search.
            column_name (str): The name of the column to search within.
            search_value (str): The value to search for in the specified column.
            print_value (bool): Whether to print the resulting DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing the search results or None if no results found.
        """
        try:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
        except Exception as e:
            print(f"Error loading table {table_name}: {e}")
            return
        
        # Construct the WHERE clause
        where_clause = f"{column_name} LIKE :{column_name}"
        
        try:
            query = text(f"SELECT * FROM {table_name} WHERE {where_clause}")
            result = self.session.execute(query, {column_name: f"%{search_value}%"})
            rows = result.fetchall()

            if rows:
                df = pd.DataFrame(rows)
                df.columns = result.keys()
                if print_value:
                    print(df)
                return df
            else:
                print(f"No results found for {search_value} in {column_name} of {table_name}")
        except Exception as e:
            print(f"Error executing search query: {e}")
    def search_by_json_field(self, table_name, json_field, key, value, file_path=None, case_sensitive=True, partial_match=False, save_to_excel=True):
        try:
            if not case_sensitive:
                value = value.lower()
                query = text(f"SELECT * FROM {table_name} WHERE LOWER(JSON_EXTRACT({json_field}, '$.{key}')) {'LIKE' if partial_match else '='} :val")
            else:
                query = text(f"SELECT * FROM {table_name} WHERE JSON_EXTRACT({json_field}, '$.{key}') {'LIKE' if partial_match else '='} :val")
            
            if partial_match:
                value = f"%{value}%"
            
            result = self.session.execute(query, {"val": value})
            rows = result.fetchall()
            
            if rows:

                df = pd.DataFrame(rows)
                df.columns = result.keys()
                
                # Flatten the nested JSON fields
                for column in df.columns:
                    if isinstance(df[column].iloc[0], dict):
                        expanded_data = df[column].apply(lambda x: get_all_key_values(x))
                        expanded_df = pd.DataFrame(expanded_data.tolist())
                        expanded_df.columns = [f"{column}.{sub_col}" for sub_col in expanded_df.columns]
                        df = df.drop(columns=[column]).join(expanded_df)
                
                if save_to_excel and file_path:
                    df.to_excel(file_path, index=False)
                    print(f"Data for {key} {value} exported to {file_path}")
                
                return df
            else:
                print(f"No results found for {value} in {key} of {json_field} in {table_name}")
        except Exception as e:
            print(f"Error executing search query: {e}")
    def scrub_tables(self, table1_name, table2_name, join_key):
        """
        Compare and clean data between two tables based on a join key.
        
        Args:
            table1_name: Name of the first table.
            table2_name: Name of the second table.
            join_key: Key used to join the tables.
            
        Returns:
            None
        """
        table1 = Table(table1_name, self.metadata, autoload_with=self.engine)
        table2 = Table(table2_name, self.metadata, autoload_with=self.engine)

        # Select records from table1 that do not exist in table2 based on the join key
        subquery = self.session.query(table2.c[join_key]).subquery()
        query = self.session.query(table1).filter(~table1.c[join_key].in_(subquery))

        records_to_delete = query.all()
        
        # Delete records from table1 that do not exist in table2
        if records_to_delete:
            for record in records_to_delete:
                self.session.delete(record)
            self.session.commit()
            print(f"Deleted {len(records_to_delete)} records from {table1_name} not found in {table2_name}.")
        else:
            print(f"No records to delete from {table1_name}. All records match {table2_name}.")

    def scrub_clients_against_addresses(self, clients_table_name, addresses_table_name):
       
        """
        Remove records from the clients table where the corresponding address is a multi-unit dwelling with solar.
        
        Args:
            clients_table_name: Name of the clients table.
            addresses_table_name: Name of the addresses table.
            
        Returns:
            None
        """
        addresses = Table(addresses_table_name, self.metadata, autoload_with=self.engine)
        clients = Table(clients_table_name, self.metadata, autoload_with=self.engine)

        # Subquery to find addresses that are multi-unit and have solar
        subquery = self.session.query(addresses.c.address).filter(
            addresses.c.multi_unit == False,
        ).subquery()

        # Select records from clients where the address matches the subquery
        query = self.session.query(clients).filter(clients.c.address.in_(subquery))

        records_to_delete = query.all()
        
        # Delete records from clients that match the subquery
        if records_to_delete:
            for record in records_to_delete:
                self.session.delete(record)
            self.session.commit()
            print(f"Deleted {len(records_to_delete)} records from {clients_table_name} where the address is a multi-unit dwelling with solar.")
        else:
            print(f"No records to delete from {clients_table_name}. All addresses are either not multi-unit or do not have solar.")
    def get_meta_datas(self):
        obj_list = ["id","baseMint","quoteMint","tokenName","tokenSymbol"]
        field_choice = get_field_choice(obj_list=obj_list,parentObject="JSON search field",object_type='JSON field')
        value = enter_value_text(typ="the",action="to filter by",parentObject=field_choice)
        return 'pool_keys' if field_choice in ['id', 'baseMint', 'quoteMint'] else 'meta_data'
    def get_json_search_vars():
        table_name = self.table_list()
        obj_list =  self.column_list()
        field_choice = get_field_choice(obj_list=obj_list,parentObject="JSON search field",object_type='JSON field')
        value = enter_value_text(typ="the",action="to filter by",parentObject=field_choice)
        queries = {"save_to_excel":{"default":"y","query":"Save to excel?"},"partial_match":{"default":"y","query":"Partial match?"},"case_sensitive":{"default":'n',"query":"Case sensitive?"}}
        for key,values in queries.items():
            queries[key]=get_user_input(values.get("query"),default=values.get('default'))
        if save_to_excel:
          output_dir = os.path.join(os.getcwd(),'output_data')
          os.makedirs(output_dir,exist_ok=True)
          fileName = f"{table_name}_{field_choice}"
          get_user_input(values.get("query"),default=values.get('default'))
          queries = {"fileName":{"query":"please enter a fileName:","default":fileName}}
          for key,values in queries.items():
              queries[key]=get_user_input(values.get("query"),default=values.get('default'))
          file_path = os.path.join(output_dir,f"{queries['fileName']}.xlsx")
        self.search_by_json_field(table_name=table_name, json_field=json_field, key=field_choice, value=value,file_path=file_path, case_sensitive=queries["case_sensitive"], partial_match=queries["partial_match"],save_to_excel=queries["save_to_excel"])
    def export_table_to_excel(self, table_name, filters=None, file_path="output.xlsx"):
        """
        Export a table to an Excel file with optional filters.
        
        Args:
            table_name (str): Name of the table to export.
            filters (dict): Optional dictionary of column filters {column_name: value}.
            file_path (str): Path to the Excel file to save.
        """
        try:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            
            query = table.select()
            if filters:
                for column, value in filters.items():
                    query = query.where(getattr(table.c, column) == value)
                    
            result = self.session.execute(query)
            rows = result.fetchall()
            excel = []
            if rows:
                for i,row in enumerate(rows):
                    if not isinstance(row,list):
                        row = list(row)
                    if isinstance(row,tuple):
                        row = list(row)
             
        
                    excel.append(flatten_json(row, parent_key='', sep='_'))
                safe_excel_save(pd.DataFrame(excel),file_path)
                print(f"Data exported to {file_path}")
            else:
                print(f"No data found in table {table_name} with given filters.")
        except Exception as e:
            print(f"Error exporting table {table_name} to Excel: {e}")

    def get_filters(self, table_name):
        """
        Get filters from the user for a specific table.
        
        Args:
            table_name (str): Name of the table to filter.
            
        Returns:
            dict: Dictionary of filters {column_name: value}.
        """
        filters = {}
        while True:
            column_name = self.column_list(table_name)
            if not column_name:
                break
            value = input(f"Enter value to filter by {column_name} (or press Enter to skip): ")
            if value:
                filters[column_name] = value
            else:
                break
        return filters

    def delete_rows_by_criteria(self, table_name, column_name, error_code=None, error_message=None):
        """
        Delete rows from the table where the specified JSON column contains an error code or message.

        Args:
            table_name (str): The name of the table to delete rows from.
            column_name (str): The name of the column containing JSON data to check.
            error_code (int, optional): The error code to match for deletion.
            error_message (str, optional): The error message to match for deletion.

        Returns:
            None
        """
        try:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            
            # Building the query based on provided criteria
            query = table.delete().where(
                (table.c[column_name].cast(JSON)["error"]["code"].as_integer() == error_code) |
                (table.c[column_name].cast(JSON)["error"]["message"].astext == error_message)
            )
            
            result = self.session.execute(query)
            self.session.commit()
            print(f"Deleted {result.rowcount} rows from {table_name} where {column_name} contained the specified error.")
        except Exception as e:
            print(f"Error deleting rows from {table_name}: {e}")
    def execute_raw_query(self, raw_query, params=None):
        """
        Execute a raw SQL query.

        Args:
            raw_query (str): The raw SQL query string to execute.
            params (dict, optional): Parameters to pass with the query.
            print_value (bool, optional): Whether to print the result. Default is False.

        Returns:
            pd.DataFrame: DataFrame containing the query results or None if no results found.
        """
        try:
            result = self.session.execute(query, params or {})
            rows = result.fetchall()
            if rows:
                df = pd.DataFrame(rows)
                return df
            else:
                print("No results found.")
        except Exception as e:
            print(f"Error executing raw query: {e}")
            return None
    def delete_table(self, table_name: str) -> None:
        """
        Delete the specified table from the database.
        
        Args:
            table_name (str): The name of the table to delete.
        
        Returns:
            None
        """
        try:
            query = text(f"DROP TABLE IF EXISTS {table_name}")
            self.session.execute(query)
            self.session.commit()
            print(f"Table '{table_name}' has been deleted.")
        except Exception as e:
            print(f"Error deleting table '{table_name}': {e}")
    def main(self):
        while True:
            print("\nMenu:")
            print("0. Exit")
            print("1. List tables")
            print("2. Search table")
            print("3. View table contents")
            print("4. List columns in a table")
            print("5. Alter column type")
            print("6. Update all entries in a column")
            print("7. Export data by key")
            print("8. Scrub tables")
            print("9. Scrub clients against addresses")
            print("10. Export table to Excel with filters")
            print("11. Delete rows with errored transaction data")
            print("12. Delete an entire table")  # New option to delete the table
            
            choice = input("Enter your choice: ")

            if choice == "0":
                print("Exiting...")
                break
            elif choice == "1":
                self.list_tables()
            elif choice == "2":
                table_name = self.table_list()
                column_name = self.column_list(table_name)
                search_value = enter_value_text(typ="", action="to search for", parentObject=column_name)
                self.search_table(table_name, column_name, search_value)
            elif choice == "3":
                table_name = self.table_list()
                table_row_count = self.session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                print(f"there are {table_row_count} selections in this table")
                if table_row_count:
                    start = get_integer_input(f"Enter start row (0-{table_row_count - 1})", 0, table_row_count - 1)
                    end = get_integer_input(f"Enter end row ({start + 1}-{table_row_count})", start + 1, table_row_count)
                    self.view_table(table_name, start, end)
            elif choice == "4":
                table_name = self.table_list()
                self.list_columns(table_name)
            elif choice == "5":
                column_name = self.column_list()
                field_choice = get_field_choice(obj_list=get_type_change_list(), parentObject="new type", object_type='type')
                self.alter_column_type(table_name, column_name, field_choice)
            elif choice == "6":
                column_name = self.column_list()
                new_value = enter_value_text(typ="new", action="for all entries", parentObject=column_name)
                self.update_all_entries(table_name, column_name, new_value)
            elif choice == "7":
                self.get_json_search_vars()
            elif choice == "8":
                table1_name, table2_name = self.table_list(), self.table_list()
                join_key = enter_value_text(typ="join key", action="to scrub tables by", parentObject=f"{table1_name} and {table2_name}")
                self.scrub_tables(table1_name, table2_name, join_key)
            elif choice == "9":
                clients_table_name = self.table_list()
                addresses_table_name = self.table_list()
                self.scrub_clients_against_addresses(clients_table_name, addresses_table_name)
            elif choice == "10":
                table_name = self.table_list()
                filters = self.get_filters(table_name)
                file_path = input("Enter the file path to save the Excel file (default: output.xlsx): ") or "output.xlsx"
                self.export_table_to_excel(table_name, filters, file_path)
            elif choice == "11":
                table_name = self.table_list()
                column_name = self.column_list(table_name)
                error_code = int(input("Enter the error code to search for (e.g., -32601): "))
                error_message = input("Enter the error message to search for (e.g., 'Method not found'): ")
                self.delete_rows_by_criteria(table_name, column_name, error_code, error_message)
            elif choice == "12":  # New choice to delete the entire table
                table_name = self.table_list()
                confirm = input(f"Are you sure you want to delete the entire table '{table_name}'? (y/n): ").lower()
                if confirm == 'y':
                    self.delete_table(table_name)
                else:
                    print("Table deletion canceled.")
        else:
            print("Invalid choice. Please try again.")

def manageDb(dbUrl=None,dbPath=None):
    db_browser = DatabaseBrowser(dbUrl=dbUrl,dbPath=dbPath)
    db_browser.main()

