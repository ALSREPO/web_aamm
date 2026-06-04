import logging

from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session
from src.utils.db_tools import get_read_db, get_write_db
from src.utils.auth import verificar_admin, usuario_obligatorio, verificar_password, obtener_password_hash, enviar_correo_cambio_estado
from src.models.models import Usuario

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])

logger = logging.getLogger("AAMM-APP-usuarios")

########################################
# /listado-completo
# /cambiar-estatus/{idusuario}
# /cambiar-password
# /cambiar-password/{idusuario}
# /eliminar-usuario/{idusuario}
# /eliminar-mi-cuenta
########################################

@router.get("/listado-completo", dependencies=[Depends(verificar_admin)])
def listar_usuarios(db: Session = Depends(get_read_db)):
    return db.query(Usuario).all()


@router.put("/cambiar-estatus/{idusuario}", dependencies=[Depends(verificar_admin)])
def cambiar_estatus(idusuario: int, nuevo_nivel: int, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):
    usuario = db.query(Usuario).filter(Usuario.idusuario == idusuario).first()
    if not usuario:
        logger.warning(f"Intento de cambio de estatus para usuario no encontrado con id {idusuario}, por admin ID_ADMIN[{admin.idusuario}]")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    try: 
        usuario.activo = nuevo_nivel
        db.commit()
        logger.info(f"Usuario ID_USUARIO[{usuario.idusuario}] actualizado a nivel {nuevo_nivel}, por admin ID_ADMIN[{admin.idusuario}]")

    except Exception as e:
        logger.error(f"Error al actualizar estatus para ID_USUARIO[{usuario.idusuario}], por admin ID_ADMIN[{admin.idusuario}]: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar el estatus")
    
    try:
        enviar_correo_cambio_estado(email_destino=usuario.email, estado=nuevo_nivel)
        logger.info(f"Correo de cambio de estado [{nuevo_nivel}] enviado para ID_USUARIO[{usuario.idusuario}]")
    except Exception as e:
        logger.error(f"Error al enviar correo de cambio de estado [{nuevo_nivel}] para ID_USUARIO[{usuario.idusuario}]: {e}")

    return {"ok": True}


@router.put("/cambiar-password", dependencies=[Depends(usuario_obligatorio)])
def cambiar_password(pass_actual: str, pass_nueva: str, db: Session = Depends(get_write_db), usuario: Usuario = Depends(usuario_obligatorio)):
    usuario = db.query(Usuario).filter(Usuario.idusuario == usuario.idusuario).first()
    # 1. Verificar pass actual
    if not verificar_password(pass_actual, usuario.password):
        logger.warning(f"Intento fallido de cambio de contraseña por introducir mal su contraseña actual para ID_USUARIO[{usuario.idusuario}]")
        raise HTTPException(status_code=400, detail=f"La contraseña actual es incorrecta.")
    
    # 2. Actualizar
    try:
        usuario.password = obtener_password_hash(pass_nueva)
        db.commit()
        logger.info(f"Contraseña actualizada para ID_USUARIO[{usuario.idusuario}]")
    except Exception as e:
        logger.error(f"Error al actualizar contraseña para ID_USUARIO[{usuario.idusuario}]: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar la contraseña")
    
    return {"detail": "Contraseña actualizada correctamente"}


@router.put("/cambiar-password/{idusuario}", dependencies=[Depends(verificar_admin)])
def admin_cambiar_password(idusuario: int, nueva_pass: str, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):    
    usuario = db.query(Usuario).filter(Usuario.idusuario == idusuario).first()
    if not usuario: 
        logger.warning(f"Intento fallido de cambio de contraseña por admin para usuario, no encontrado con id {idusuario}")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Hasheamos la nueva contraseña (usa tu función de auth)
    try:
        usuario.password = obtener_password_hash(nueva_pass)
        db.commit()
        logger.info(f"Contraseña actualizada para ID_USUARIO[{usuario.idusuario}], por admin ID_ADMIN[{admin.idusuario}]")
    except Exception as e:
        logger.error(f"Error al actualizar contraseña por admin para ID_USUARIO[{usuario.idusuario}], por admin ID_ADMIN[{admin.idusuario}]: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar la contraseña")

    return {"ok": True}


@router.delete("/eliminar-usuario/{idusuario}", dependencies=[Depends(verificar_admin)])
def eliminar_usuario(idusuario: int, db: Session = Depends(get_write_db), admin: Usuario = Depends(usuario_obligatorio)):
    # Evitar que el admin se borre a sí mismo
    if admin.idusuario == idusuario:
        logger.warning(f"Intento de eliminación de cuenta por admin para su propia cuenta: ID_ADMIN[{admin.idusuario}]")
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta de administrador")

    usuario = db.query(Usuario).filter(Usuario.idusuario == idusuario).first()
    
    if not usuario:
        logger.warning(f"Intento de eliminación de usuario no encontrado con id {idusuario}")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    try:
        db.delete(usuario)
        db.commit()
        logger.info(f"Usuario eliminado: ID_USUARIO[{usuario.idusuario}], por admin ID_ADMIN[{admin.idusuario}]")
    except Exception as e:
        logger.error(f"Error al eliminar usuario ID_USUARIO[{usuario.idusuario}]: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar el usuario")

    return {"ok": True, "message": "Usuario eliminado permanentemente"}


@router.delete("/eliminar-mi-cuenta")
def eliminar_mi_cuenta(
    response: Response, 
    db: Session = Depends(get_write_db), 
    usuario: Usuario = Depends(usuario_obligatorio)
):
    """Permite al usuario logueado borrar su propia cuenta permanentemente"""
    # 1. Buscamos al usuario en la base de datos
    db_user = db.query(Usuario).filter(Usuario.idusuario == usuario.idusuario).first()
    
    if not db_user:
        logger.warning(f"Intento de auto-eliminación de cuenta no encontrada: ID_USUARIO[{usuario.idusuario}]")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    try:
        # 2. Lo eliminamos de la Base de Datos
        db.delete(db_user)
        db.commit()
        logger.info(f"El usuario eliminó su propia cuenta de forma permanente: ID_USUARIO[{db_user.idusuario}]")
        
        # 3. Limpiamos la cookie de sesión del navegador para desloguearlo
        response.delete_cookie(key="access_token")
        
    except Exception as e:
        logger.error(f"Error al auto-eliminar la cuenta del usuario ID_USUARIO[{db_user.idusuario}]: {e}")
        raise HTTPException(status_code=500, detail="Error interno al eliminar la cuenta")

    return {"ok": True, "message": "Tu cuenta ha sido eliminada permanentemente"}