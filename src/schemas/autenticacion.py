from pydantic import BaseModel, EmailStr

# --- Esquemas de Autenticación ---

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str