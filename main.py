from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import (
        create_engine,
        MetaData,
        Table,
        Column,
        String,
        Integer,
        Float,
        insert,
        inspect,
        text
        )

engine = create_engine('sqlite:///local.db')

metadata_obj = MetaData()

def insert_rows_into_table(rows, table, engine=engine):
    for row in rows:
        stmt = insert(table).values(**row)
        with engine.begin() as connection:
            connection.execute(stmt)

table_name = 'receipts'
receipts = Table(
        table_name,
        metadata_obj,
        Column('receipt_id', Integer, primary_key=True),
        Column('customer_name', String(20), primary_key=True),
        Column('price', Float),
        Column('tip', Float),
        )



rows = [
        {"receipt_id": 1, "customer_name": "Alan Payne", "price": 12.06, "tip": 1.20},
        {"receipt_id": 2, "customer_name": "Alex Mason", "price": 23.86, "tip": 0.24},
        {"receipt_id": 3, "customer_name": "Woodrow Wilson", "price": 53.43, "tip": 5.43},
        {"receipt_id": 4, "customer_name": "Margaret James", "price": 21.11, "tip": 1.00},
        ]


table_name = 'waiters'
waiters = Table(
        table_name,
        metadata_obj,
        Column('receipt_id', Integer, primary_key=True),
        Column('waiter_name', String(16), primary_key=True),
        )


metadata_obj.create_all(engine)
insert_rows_into_table(rows, receipts)

rows = [
        {"receipt_id": 1, "waiter_name": "Pakita"},
        {"receipt_id": 2, "waiter_name": "Lolita"},
        {"receipt_id": 3, "waiter_name": "Lolita"},
        {"receipt_id": 4, "waiter_name": "Doidita"},
        ]

insert_rows_into_table(rows, waiters)

inspector = inspect(engine)

updated_description = """Allows you to perform SQL queries on the table. Beware that this tool's output is a string representation of the execution output.
It can use the following tables:"""

for table in ['receipts', 'waiters']:
    col_info = [(col['name'], col['type']) for col in
                inspector.get_columns(table)]
    table_description = f"Table '{table}':\n"
    table_description += "Columns:\n" + "\n".join([f'    - {name}: {col_type}' for
                                              name, col_type in col_info])

    updated_description += "\n\n" + table_description
    print(table_description)

from smolagents import tool, Tool

class SqlEngine(Tool):
    name = 'sql_engine'
    description=updated_description
    inputs = {
            "query": {
                "type": "string",
                "description": "The query to perform. This should be correct SQL.",
                }
            }
    output_type = 'string'

    def forward(self, query: str) -> str:
        output = ""
        with engine.connect() as con:
            rows = con.execute(text(query))
            for row in rows:
                output += "\n" + str(row)
            return output
sql_engine = SqlEngine()
from smolagents import CodeAgent, InferenceClientModel

agent = CodeAgent(
        tools=[sql_engine],
        model=InferenceClientModel(model_id='Qwen/Qwen3-Next-80B-A3B-Thinking'),
        )
agent.run(""" Which waiter got more money from tips? """)
