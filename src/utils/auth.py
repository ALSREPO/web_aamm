from passlib.context import CryptContext


# Configuración de Passlib para usar SHA-512
# 'crypt_dist' asegura que usemos implementaciones seguras
pwd_context = CryptContext(schemes=["sha512_crypt"], deprecated="auto")



def verificar_password(plain_password, hashed_password):
    """Compara la contraseña en plano con el hash de la BBDD"""
    return pwd_context.verify(plain_password, hashed_password)