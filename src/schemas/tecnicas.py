from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class DisciplinaBase(BaseModel):
    disciplina: str
    iddisciplina: int
    class Config:
        from_attributes = True

class EtiquetaBase(BaseModel):
    etiqueta: str
    idetiqueta: int
    orden: int
    
    class Config:
        from_attributes = True


class TecnicaRead(BaseModel):
    idtecnica: int
    nombre: str
    descripcion: str
    fecha: date 
    cantidad_videos: int
    disciplinas: List[DisciplinaBase] = []
    etiquetas: List[EtiquetaBase] = []
    class Config:
        from_attributes = True

# Para el detalle de cada técnica
class VideoRead(BaseModel):
    #idvideo: int
    video: str  # Aquí guardaremos el "nombre.mp4"
    #orden: int
    
    class Config:
        from_attributes = True


# vista de detalle de una técnica
class TecnicaDetalle(TecnicaRead):
    videos: List[VideoRead] = [] # Aquí incluimos la lista de vídeos

# listado de tecnicas
class PaginaTecnicas(BaseModel):
    total: int
    resultados: List[TecnicaRead] # Reutiliza el TecnicaRead que ya tenemos

    class Config:
        from_attributes = True

# crear nuevas técnicas
class TecnicaCreate(BaseModel):
    nombre: str
    descripcion: str
    fecha: date
    disciplinas_ids: List[int] = []
    etiquetas_ids: List[int] = []
    videos_nombres: List[str] = [] # Ejemplo: ["patada1.mp4", "detalle_giro.mp4"]

    class Config:
        from_attributes = True