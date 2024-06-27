import sqlalchemy as _sqlalchemy
import sqlalchemy.ext.declarative as _declarative
import sqlalchemy.orm as _orm


db_url = "sqlite:///dbfile.db"

engine = _sqlalchemy.create_engine(db_url, connect_args={"check_same_thread":False},  echo=True)

Session = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = _declarative.declarative_base()