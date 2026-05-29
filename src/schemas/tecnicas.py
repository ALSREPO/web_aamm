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

# listado de tecnicas
class PaginaTecnicas(BaseModel):
    total: int
    resultados: List[TecnicaRead] # Reutiliza el TecnicaRead que ya tenemos

    class Config:
        from_attributes = True