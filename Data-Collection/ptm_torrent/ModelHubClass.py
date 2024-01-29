import petl as etl
from petl import Table
import logging
from typing import List, Mapping

# The purpose of the ModelHub is to provide a class base for verification that
# transforms are valid and match the final database schema.  This is done by
# defining the final schema then using etl.validate() [https://petl.readthedocs.io/en/stable/transform.html#validation]
# to verify that the transforms match the schema

class ModelHubClass():
    name : str = "ModelHubClass"
    data_path: str

    transform_constraints : Mapping[str, dict]   | None = None
    transform_headers     : Mapping[str, tuple]  | None = None
    mandatory_tables      : List[str]            | None = None
    transformed_data      : Mapping[str, Table]  | None = None

    def __init__(self):
        pass

    def extract(self):
        pass

    def verify(self):
        self.verify_extraction()
        self.verify_transformations()

    def verify_extraction(self):
        pass

    def verify_transformations(self, transformed_data: Mapping[str, Table] | None = None):
        for table in self.mandatory_tables:
            if table not in transformed_data:
                logging.error(f"Missing {table} table in {self.name} transformed data")
                return

        for table_name, table in transformed_data.items():
            constraints = self.transform_constraints[table_name]
            header = self.transform_headers[table_name]
            problems = etl.validate(table, constraints = constraints, header = header)
            logging.info(f"Total {self.name} {table_name} Errors: {problems.nrows()}")
            logging.debug(f"{self.name} {table_name} Errors:\n{problems.lookall()}")

    def load_csv(self, suffix: str = ""):
        for table_name, table in self.transformed_data.items():
            print(f"Saving table {table_name}")
            etl.tocsv(table, f"{self.data_path}/csv/{self.name}_{table_name}_{suffix}.csv")

    def load_json(self, suffix: str = ""):
        for table_name, table in self.transformed_data.items():
            print(f"Saving table {table_name}")
            etl.tojson(table, f"{self.data_path}/json/{self.name}_{table_name}_{suffix}.json")

    def store(self):
        for table_name, table in self.transformed_data.items():
            print(table_name)
            etl.tojson(table, f"{self.data_path}/csv/{self.name}_{table_name}.json", default=str)

    def frequency(table: Table):
        freq = table.nrows()
        headers = table.header()
        print("Non-Null Value Frequency:")
        none_freq = (table.progress(freq+1, prefix=f"field {headers.index(field)} of {len(headers)}: ").valuecount((field), None) for field in etl.header(table))
        none_freq_table = etl.fromcolumns((etl.header(table), none_freq), header=["field", "none_freq"])
        none_freq_table = etl.unpack(none_freq_table, "none_freq", newfields=("amount", "freq"))
        none_freq_table = none_freq_table.convert("amount", lambda v: freq - v)
        none_freq_table = none_freq_table.convert("freq", lambda v: 1 - v)
        none_freq_table = etl.sort(none_freq_table, "freq", reverse=True)
        print(none_freq_table.lookall())