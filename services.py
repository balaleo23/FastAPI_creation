import database as _database
import models as _models
import sqlalchemy.orm as _orm
import schemas as _schemas
import email_validator as _email_validator
import fastapi as _fastapi
import passlib.hash as _hash
import jwt as _jwt
import fastapi.security as _security
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException


_JWT_SECRET = "myjwtsecret"
oauth2schema = _security.OAuth2PasswordBearer("api/v1/login")

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


create_db()


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

async def login(email : str , password : str , db : _orm.session):
    
    
    db_user = await getUserByEmail(email=email, db=db)
    #if user email is not found
    if not db_user:
        return False

    #if user password is not found    
    if not db_user.password_verfication(password= password):
        return False
    
    return db_user

async def current_user (db: _orm.session = _fastapi.Depends(get_db) , 
                        token :str = _fastapi.Depends(oauth2schema)):    
    try:
        payload = _jwt.decode(token, _JWT_SECRET,  algorithms=["HS256"])  
        #get user by id from payload (id and phone is already available in userpayload in token)
        db_user = db.query(_models.UserModel).filter(_models.UserModel.id == payload["id"]).first()
    except:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    #if everything okay return dto version of the user
    return _schemas.UserResponse.from_orm(db_user)  




async def create_post(user : _schemas.UserRequest , db : _orm.session,
                      post : _schemas.PostRequest):
    try:

        post = _models.PostModel(
            **post.dict(),userid = user.id
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        #convert the post model to Post DTO/Schemas and return to API layer
        return _schemas.PostResponse.from_orm(post)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while creating the post.")


async def get_posts_by_user(user: _schemas.UserResponse, db: _orm.session):
    try:
        posts = db.query(_models.PostModel).filter_by(userid=user.id).all()
        # convert each post model to post schema and make a list to be returned
        return list(map(_schemas.PostResponse.from_orm, posts))
    except SQLAlchemyError as e:
        print(f" error in services: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while retriving the post.")


async def get_posts_details(post_id: int, 
                            db: _orm.session):
    try :
        db_post = db.query(_models.PostModel).filter_by(id=post_id).first()
        if db_post is None: 
            raise HTTPException(status_code=404, detail="Post not found")

        return _schemas.PostResponse.from_orm(db_post)
    except SQLAlchemyError as e:
        print(f" error in services: {str(e)}")
        db.rollback()



async def getUserDetails(userid: int, 
                            db: _orm.session):
    try :
        db_user = db.query(_models.UserModel).filter_by(id=userid).first()
        if db_user is None: 
            raise HTTPException(status_code=404, detail="Services: User not found")

        return _schemas.UserResponse.from_orm(db_user)
    except SQLAlchemyError as e:
        print(f" error in services: {str(e)}")
        db.rollback()


async def delete_post(post_id: int, db: _orm.session):
        delete_post = db.query(_models.PostModel).filter_by(id=post_id).delete()
        print(delete_post)
        if delete_post == 0:
            raise HTTPException(status_code=404, detail="Post not found")
        db.commit()
        return 'post is deleted successfully'
    

async def update_post(post_id: int, post: _schemas.PostRequest, db: _orm.session):
    try:
        db_post = db.query(_models.PostModel).filter_by(id=post_id).first()
        if db_post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        db_post.post_title = post.post_title
        db_post.post_description = post.post_description
        db_post.image_path = post.image_path
        db.commit()
        return _schemas.PostResponse.from_orm(db_post)

    except SQLAlchemyError as e:
        print(f" error in services: {str(e)}")
        db.rollback()   

async def get_all_posts(db: _orm.session):
    posts = db.query(_models.PostModel).all() 
    if posts is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return list(map(_schemas.PostResponse.from_orm, posts))