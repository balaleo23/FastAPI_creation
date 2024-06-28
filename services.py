import database as _database
import models as _models
import sqlalchemy.orm as _orm
import schemas as _schemas
import email_validator as _email_validator
import fastapi as _fastapi
import passlib.hash as _hash
import jwt as _jwt

_JWT_SECRET = "myjwtsecret"


def create_db():
    return _database.Base.metadata.create_all(bind= _database.engine)



def get_db():
    db = _database.Session()
    try:
        yield db
    finally:
        db.close()


async def create_token(user: _models.UserModel):
    #convert the user model to schemas
    user_schemas = _schemas.UserResponse.from_orm(user)
    user_dict = user_schemas.dict()
    del user_dict["created_at"]
    token = _jwt.encode(user_dict, _JWT_SECRET)
    return dict(access_token =token , token_type = "bearer")




    pass

async def getUserByEmail(email : str , db : _orm.session):
    return db.query(_models.UserModel).filter(_models.UserModel.email == email).first()
    # return db.query(_models.UserModel).filter_by(_models.UserModel.email ==email).first()


async def create_user(user : _schemas.UserRequest , db : _orm.session):

    try:
        is_valid = _email_validator.validate_email(user.email)
        if not is_valid:
            raise ValueError("Invalid email address")
    except _email_validator.EmailNotValidError:
        _fastapi.HTTPException(status_code=400, detail="Provide Email Id in proper format")

    # convert normal password to hashed password
    hashed_password = _hash.bcrypt.hash(user.password)
    #create the usermodel to save
    user_object = _models.UserModel(
        email = user.email,
        name = user.name,
        phone = user.phone,
        password_hash = hashed_password

    )

    db.add(user_object)
    db.commit()
    db.refresh(user_object)
    return user_object

        




create_db()
