from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Extra


class ErrorResponse(BaseModel):
    error: Optional[Union[str, Dict, List]] = "Unknown error"
    error_code: str = "ERROR"


class ORMSchema(BaseModel):
    class Config:
        orm_mode = True
        extra = Extra.ignore
