import database as _database
import models as _models


def create_db():
    return _database.Base.metadata.create_all(bind= _database.engine)



def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


create_db()
