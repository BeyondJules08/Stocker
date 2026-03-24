from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

from app.database import get_db
from app.dependencies import create_access_token, get_current_user
from app.models import Usuario
from app.schemas import TokenResponse, UsuarioOut

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    if not user or not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not check_password_hash(user.password_hash, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.ultimo_acceso = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token({"sub": str(user.id), "rol": user.rol.nombre})
    return TokenResponse(
        access_token=token,
        rol=user.rol.nombre,
        nombre=user.nombre,
    )


@router.get("/me", response_model=UsuarioOut)
def me(current_user: Usuario = Depends(get_current_user)):
    return current_user
