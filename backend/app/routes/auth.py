from fastapi import APIRouter
from backend.app.db.database import SessionLocal
from backend.app.db.models import User
from backend.app.models.chat_models import SignupRequest, LoginRequest
from backend.app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter()


@router.post("/signup")
def signup(request: SignupRequest):
    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_user:
        db.close()
        return {
            "message": "Email already registered"
        }

    user = User(
        name=request.name,
        email=request.email,
        password=hash_password(request.password)
    )

    db.add(user)
    db.commit()
    db.close()

    return {
        "message": "User created successfully"
    }


@router.post("/login")
def login(request: LoginRequest):
    db = SessionLocal()

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        db.close()
        return {
            "message": "Invalid email or password"
        }

    if not verify_password(request.password, user.password):
        db.close()
        return {
            "message": "Invalid email or password"
        }

    token = create_access_token({
        "sub": user.email
    })

    db.close()

    return {
        "access_token": token,
        "token_type": "bearer"
    }