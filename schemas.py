from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CarBase(BaseModel):
    region: str
    contact: Optional[str] = None
    description: Optional[str] = None

class CarCreate(CarBase):
    pass

class CarUpdate(BaseModel):
    region: Optional[str] = None
    contact: Optional[str] = None
    description: Optional[str] = None

class Car(CarBase):
    id: int
    image_base64: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CarDetails(Car):
    contact: Optional[str] = None
    description: Optional[str] = None



# 管理员相关schemas
class AdminLogin(BaseModel):
    username: str
    password: str

class AdminToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 站点配置相关schemas
class SiteConfigBase(BaseModel):
    config_key: str
    config_value: str
    description: Optional[str] = None

class SiteConfigCreate(SiteConfigBase):
    pass

class SiteConfigUpdate(BaseModel):
    config_value: str
    description: Optional[str] = None

class SiteConfig(SiteConfigBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 首页密码验证
class HomepagePasswordVerify(BaseModel):
    password: str

class HomepagePasswordSet(BaseModel):
    password: str 