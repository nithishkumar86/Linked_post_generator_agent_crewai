from pydantic import BaseModel

class PostState(BaseModel):
    topic: str = ""
    feedback: str = ""
    iteration: int = 0
    approved: bool = False
    post_content: str = ""