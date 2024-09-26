from pydantic import BaseModel


class PageInfo(BaseModel):
    name: str
    id: str  # notion page id
    uid: int = None  # database uid (for url, md file name)


class MDInfo(BaseModel):
    filepath: str
    content: str
