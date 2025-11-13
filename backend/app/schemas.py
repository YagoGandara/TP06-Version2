from pydantic import BaseModel, ConfigDict

class TodoOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    done: bool
    model_config = ConfigDict(from_attributes=True)  

class TodoIn(BaseModel):
    title: str
    description: str | None = None
