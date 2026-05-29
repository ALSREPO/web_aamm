from pydantic import BaseModel

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