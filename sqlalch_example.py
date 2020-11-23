#'postgresql+psycopg2://admin:12345678M@127.0.0.1:5432/db7165.ru'
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

def main():
    engine = create_engine('postgresql+psycopg2://admin:12345678M@127.0.0.1:5432/db7165.ru', echo=True)
    meta = MetaData()

    students = Table(
        'students', meta,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('lastname', String),
    )
    meta.create_all(engine)

if __name__ == "__main__":
    main()