from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from src.models import Base
# Switch to Mysql
# database_name = os.environ.get('DATABASE_NAME')
# database_password = os.environ.get('DATABASE_PASSWORD')
# database_author = os.environ.get('DATABASE_AUTHOR')

Base.metadata.create_all(
    create_engine(
        'sqlite:///main.sqlite'
    )
)


class DatabaseContextManager:
    def __init__(self):
        self.databasefilename: str = 'sqlite:///test.db' if current_app.config['ENV'] == 'testing' else f'sqlite:///main.sqlite'
        self.engine = create_engine(self.databasefilename, echo=True)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def __enter__(self):
        self.session = self.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"{exc_type}")
            self.session.rollback()
            self.session.close()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
