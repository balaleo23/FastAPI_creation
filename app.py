import fastapi as _fastapi
import fastapi.security as _security
import uvicorn as _uvicorn
import sqlalchemy.orm as _orm
import database as _database
import schemas as _schemas
import services as _services

app = _fastapi.FastAPI()

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
