from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DBEngine:
    def __init__(self, db_name: str, db_user: str, db_pass: str, db_port: str):
        self.db_url = (
            f"postgresql+psycopg2://{db_user}:{db_pass}@localhost:{db_port}/{db_name}"
        )
        self.engine = create_engine(self.db_url)
        self.session = sessionmaker(bind=self.engine)()
