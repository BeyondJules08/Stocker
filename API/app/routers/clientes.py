from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_rol
from app.models import Cliente, Usuario
from app.schemas import ClienteCreate, ClienteOut, ClienteUpdate

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("", response_model=list[ClienteOut])
def listar_clientes(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return db.query(Cliente).filter(Cliente.activo == True).order_by(Cliente.razon_social).all()


@router.get("/{cliente_id}", response_model=ClienteOut)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    cliente = db.get(Cliente, cliente_id)
    if not cliente or not cliente.activo:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.post("", response_model=ClienteOut, status_code=status.HTTP_201_CREATED)
def crear_cliente(
    data: ClienteCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("operativo", "gerente")),
):
    dup = db.query(Cliente).filter(Cliente.rfc == data.rfc).first()
    if dup:
        raise HTTPException(status_code=400, detail="RFC ya registrado")
    cliente = Cliente(**data.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.put("/{cliente_id}", response_model=ClienteOut)
def actualizar_cliente(
    cliente_id: int,
    data: ClienteUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("operativo", "gerente")),
):
    cliente = db.get(Cliente, cliente_id)
    if not cliente or not cliente.activo:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(cliente, field, value)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_rol("gerente")),
):
    cliente = db.get(Cliente, cliente_id)
    if not cliente or not cliente.activo:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente.activo = False
    db.commit()
