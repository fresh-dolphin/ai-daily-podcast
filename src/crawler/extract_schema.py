from pydantic import BaseModel

class ExtractSchema(BaseModel):
    content: str
    category: str