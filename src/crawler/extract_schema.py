from pydantic import BaseModel

class ExtractSchema(BaseModel):
    title: str
    content: str
    publish_date: str