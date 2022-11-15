from pydantic import BaseModel

class UserPreference(BaseModel):
    userId:int
    name:str
    rating:float