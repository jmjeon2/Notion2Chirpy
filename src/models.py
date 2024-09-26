from pydantic import BaseModel


class PageInfo(BaseModel):
    name: str
    id: str


class MDInfo(BaseModel):
    filepath: str
    content: str
