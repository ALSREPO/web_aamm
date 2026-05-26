from pydantic import BaseModel, EmailStr

# --- Esquemas de Autenticación ---

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str

class UsuarioCreate(UsuarioBase):
    password: str

class Mensaje(BaseModel):
    message: str