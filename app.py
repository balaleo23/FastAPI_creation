import fastapi as _fastapi
import fastapi.security as _security
import uvicorn as _uvicorn
import sqlalchemy.orm as _orm
import database as _database
import schemas as _schemas
import services as _services
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost",  # Allow local development
    "http://localhost:8000",  # Allow local server
    # Add other origins as needed
]



logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


app = _fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/users")
async def register_user(user: _schemas.UserRequest ,db : _orm.Session = _fastapi.Depends(_services.get_db)):
    db_user = await _services.getUserByEmail(email=user.email, db=db) 
    #if user found throw exception
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already in use")
    
    #call to check if the user with email exists
    #create user and token
    db_user = await _services.create_user(user = user, db=db)
    return await _services.create_token(user=db_user)


@app.post("/api/v1/login")
async def login(
    form_data : _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
    db : _orm.Session = _fastapi.Depends(_services.get_db)
):
    db_user = await _services.login(form_data.username, form_data.password, db)

    #if invalid user name and password
    if not db_user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Email or Password")

    #once the login is succe create the token
    return await _services.create_token(user=db_user)

 
@app.get("/api/v1/current_user", response_model=_schemas.UserResponse)
async def get_current_user(user: _schemas.UserResponse = _fastapi.Depends(_services.current_user)):
    return user

@app.post("/api/v1/posts", response_model=_schemas.PostResponse)
async def create_post(post_request: _schemas.PostRequest, 
                      user: _schemas.UserResponse = _fastapi.Depends(_services.current_user), 
                      db : _orm.Session = _fastapi.Depends(_services.get_db)):
    try:
        return await _services.create_post(user=user, db=db, post=post_request)
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Database error"})
   
        

@app.get("/api/v1/get_posts", response_model=list[_schemas.PostResponse])
async def get_posts(    
        user: _schemas.UserRequest = _fastapi.Depends(_services.current_user),
        db : _orm.Session = _fastapi.Depends(_services.get_db)):
    try:
        return await _services.get_posts_by_user(user=user, db=db)
    except Exception as e:
        print(f"Error in app : {str(e)}")
        logging.error(f"Database error: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Database error"})
    

@app.get("/api/v1/{post_id}/post", response_model=_schemas.PostResponse)
async def get_post_details(post_id: int, db : _orm.Session = _fastapi.Depends(_services.get_db)):
        db_posts = await _services.get_posts_details(post_id=post_id, db=db)
        if db_posts is None:
            raise _fastapi.HTTPException(status_code=404, detail="Post not found")
        return db_posts
    # except Exception as e:
    #     print(f"Error in app : {str(e)}")
    #     logging.error(f"Database error: {str(e)}")
    #     return JSONResponse(status_code=500, content={"message": "Database error"})

@app.get("/api/v1/allusers", response_model=_schemas.UserResponse)
async def get_user_details(userid: int, db : _orm.Session = _fastapi.Depends(_services.get_db)):
        dp_users = await _services.getUserDetails(userid=userid, db=db)
        if dp_users is None:
            raise _fastapi.HTTPException(status_code=404, detail="Users not found")
        return dp_users



@app.delete("/api/v1/{post_id}/post")
async def delete_post(post_id: int, 
                      db : _orm.Session = _fastapi.Depends(_services.get_db),
                      user : _schemas.UserResponse = _fastapi.Depends(_services.current_user)):
       delete_db_posts= await _services.delete_post(post_id=post_id, db=db)
       return delete_db_posts


@app.put("/api/v1/{post_id}/post", response_model=_schemas.PostResponse)
async def update_post(post_id: int, post_request: _schemas.PostRequest, 
                      db : _orm.Session = _fastapi.Depends(_services.get_db),
                      user : _schemas.UserResponse = _fastapi.Depends(_services.current_user)):
    try:
        return await _services.update_post(post_id=post_id, post=post_request, db=db)
    except Exception as e:
        print(f"Error in app : {str(e)}")
        logging.error(f"Database error: {str(e)}")


@app.get("/api/v1/get_all_posts", response_model=list[_schemas.PostResponse])
async def getallposts(db : _orm.Session = _fastapi.Depends(_services.get_db)):
    try:
        return await _services.get_all_posts(db=db)
    except Exception as e:
        print(f"Error in app : {str(e)}")
        logging.error(f"Database error: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Database error"})
    