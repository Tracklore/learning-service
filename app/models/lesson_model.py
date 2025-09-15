from pydantic import BaseModel
from typing import List, Optional

class Lesson(BaseModel):
    lesson_id: str
    title: str
    content: str
    resources: Optional[List[str]] = None  # URLs, PDFs, videos
    embedding_vector: Optional[List[float]] = None  # For semantic search
