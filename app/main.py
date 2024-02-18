from fastapi import FastAPI, Depends, status, Request, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from . import models, utils, oauth2, schemas
from .database import get_db
import re

app = FastAPI()

# Configure CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants for error messages
INVALID_EMAIL_MESSAGE = "The email address is not valid. It must have exactly one @-sign."
INVALID_CREDENTIALS_MESSAGE = "Invalid credentials."
EMAIL_ALREADY_REGISTERED_MESSAGE = "Email already registered."
EMAIL_AND_PASSWORD_REQUIRED = "Both email and password are required."
INVALID_PASSWORD = "The password policy requires a minimum length of 8 characters and at least one lowercase letter, one uppercase letter, and one digit."

# Password policy rules
PASSWORD_MIN_LENGTH = 8
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).*$")

# Exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_response = {"detail": f"value is not a valid email address: {INVALID_EMAIL_MESSAGE}"}
    return JSONResponse(content=error_response, status_code=422)

# Login route
@app.post("/login", response_model=dict)
def log_in(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.func.lower(models.User.email) == user_credentials.username.lower()).first()

    if not user or not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS_MESSAGE)

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# User creation route
@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Convert email to lowercase for case-insensitive comparison
    user_email_lower = user.email.lower()

    existing_user = db.query(models.User).filter(models.func.lower(models.User.email) == user_email_lower).first()

    if existing_user:
        raise HTTPException(status_code=409, detail=EMAIL_ALREADY_REGISTERED_MESSAGE)

    if not user.email or not user.password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=EMAIL_AND_PASSWORD_REQUIRED)

    # Validate password against policy
    if len(user.password) < PASSWORD_MIN_LENGTH or not PASSWORD_REGEX.match(user.password):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=INVALID_PASSWORD)

    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    user.email = user_email_lower

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
