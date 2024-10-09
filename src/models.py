from typing import List, Optional
import yaml

from pydantic import BaseModel


class PageInfo(BaseModel):
    name: str
    id: str  # notion page id
    uid: int = None  # database uid (for url, md file name)


class MDInfo(BaseModel):
    filename: str  # YYYY-MM-DD-UID.md
    content: str  # markdown content


class FrontMatter(BaseModel):
    # essential
    title: str
    categories: List[str]
    tags: List[str]
    date: str

    # optional
    uid: Optional[int] = None
    math: Optional[bool] = False
    mermaid: Optional[bool] = False

    def to_md(self):
        _dict = self.dict()

        # remove math, mermaid if False
        if not _dict['math']:
            _dict.pop('math')
        if not _dict['mermaid']:
            _dict.pop('mermaid')

        _yaml = yaml.dump(_dict, default_flow_style=False, allow_unicode=True)
        return f"---\n{_yaml}---"
