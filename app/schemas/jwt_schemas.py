from pydantic import BaseModel, Field, ConfigDict, field_validator



class RefreshTokenRequestSchema(BaseModel):
    """
схема для проверки выдаваемого refresh Токена юзеру
    """
    refresh_token : str
    
    


