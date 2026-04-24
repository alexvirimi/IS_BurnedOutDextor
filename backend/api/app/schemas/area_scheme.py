from pydantic import BaseModel
from uuid import UUID
from fastapi import Form #Debes importar esta cosa bonita de aqui
class AreaCreate (BaseModel):
    name:str
    @classmethod 
    def as_form(cls, name:str = Form (...)): #cls es la forma generica de referirse a la clase actual (AreaCreate)
        #Dentro de la funcion as form se deben poner cada uno de los campos que se deben/quieren rellenar
        return cls(name=name) #se retorna la instancia de la clase con los campos que se quieren rellenar, en este caso solo el nombre del area, el id se genera automaticamente al crear el area en la base de datos
        #se puede traducir como Return AreaCreate(name=name) pero se prefiere usar cls para mantener la flexibilidad en caso de que se cambie el nombre de la clase en el futuro (no es probable pero buenas practicas and those mmdas)
        #Idk why pero se debe hacer pip install python-multipart para que funcione el Form en FastAPI
class AreaResponse(BaseModel):
    id: UUID
    name: str        
    model_config = {"from_attributes": True} 