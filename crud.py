from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, UploadFile
from passlib.context import CryptContext
import models
import schemas
from storage_service import storage_service

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_cars(db: Session, region: str = None, page: int = 1, limit: int = 20):
    """获取车辆列表（支持分页）"""
    query = db.query(models.Car)
    if region:
        query = query.filter(models.Car.region == region)
    
    # 计算总数
    total = query.count()
    
    # 分页查询
    cars = query.order_by(models.Car.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return {
        "cars": [
            {
                "id": car.id,
                "region": car.region,
                "image_base64": car.image_base64,
                "contact": car.contact,
                "description": car.description,
                "created_at": car.created_at
            }
            for car in cars
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "has_more": (page * limit) < total
    }

def get_car_by_id(db: Session, car_id: int):
    """通过ID获取车辆"""
    return db.query(models.Car).filter(models.Car.id == car_id).first()

async def create_car(db: Session, region: str, contact: str, description: str, image: UploadFile):
    """创建新车辆记录"""
    # 上传图片并转换为BASE64
    upload_result = await storage_service.upload_file(image)
    
    # 创建车辆记录
    db_car = models.Car(
        region=region,
        image_base64=upload_result["base64_data"],
        contact=contact,
        description=description
    )
    
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    
    return {
        "id": db_car.id,
        "region": db_car.region,
        "image_base64": db_car.image_base64,
        "contact": db_car.contact,
        "description": db_car.description,
        "created_at": db_car.created_at
    }



def get_car_details(db: Session, car_id: int):
    """获取车辆详情"""
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="车辆不存在")
    
    return {
        "id": car.id,
        "region": car.region,
        "image_base64": car.image_base64,
        "contact": car.contact,
        "description": car.description,
        "created_at": car.created_at
    }

async def delete_car(db: Session, car_id: int):
    """删除车辆"""
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="车辆不存在")
    
    # BASE64存储不需要删除文件
    db.delete(car)
    db.commit()
    
    return {"message": "车辆删除成功"}

async def update_car(db: Session, car_id: int, region: str = None, 
                    contact: str = None, description: str = None, image: UploadFile = None):
    """更新车辆信息"""
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="车辆不存在")
    
    # 更新字段
    if region:
        car.region = region
    if contact is not None:
        car.contact = contact
    if description is not None:
        car.description = description
    
    # 更新图片
    if image:
        # 上传新图片并转换为BASE64
        upload_result = await storage_service.upload_file(image)
        car.image_base64 = upload_result["base64_data"]
    
    db.commit()
    db.refresh(car)
    
    return {
        "id": car.id,
        "region": car.region,
        "image_base64": car.image_base64,
        "contact": car.contact,
        "description": car.description,
        "created_at": car.created_at
    }

# 用户相关CRUD操作
def get_user_by_username(db: Session, username: str):
    """通过用户名获取用户"""
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    """创建新用户"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    """验证用户"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

# 站点配置相关CRUD操作
def get_site_config(db: Session, config_key: str):
    """获取站点配置"""
    return db.query(models.SiteConfig).filter(models.SiteConfig.config_key == config_key).first()

def create_site_config(db: Session, config: schemas.SiteConfigCreate):
    """创建站点配置"""
    # 检查是否已存在
    existing = get_site_config(db, config.config_key)
    if existing:
        raise HTTPException(status_code=400, detail="配置项已存在")
    
    # 如果是密码配置，需要加密
    config_value = config.config_value
    if config.config_key == "homepage_password":
        config_value = get_password_hash(config.config_value)
    
    db_config = models.SiteConfig(
        config_key=config.config_key,
        config_value=config_value,
        description=config.description
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def update_site_config(db: Session, config_key: str, config_update: schemas.SiteConfigUpdate):
    """更新站点配置"""
    db_config = get_site_config(db, config_key)
    if not db_config:
        raise HTTPException(status_code=404, detail="配置项不存在")
    
    # 如果是密码配置，需要加密
    config_value = config_update.config_value
    if config_key == "homepage_password":
        config_value = get_password_hash(config_update.config_value)
    
    db_config.config_value = config_value
    if config_update.description is not None:
        db_config.description = config_update.description
    
    db.commit()
    db.refresh(db_config)
    return db_config

def verify_homepage_password(db: Session, password: str):
    """验证首页密码"""
    config = get_site_config(db, "homepage_password")
    if not config:
        # 如果没有设置密码，默认允许访问
        return True
    
    return verify_password(password, config.config_value)

def init_default_homepage_password(db: Session):
    """初始化默认首页密码"""
    config = get_site_config(db, "homepage_password")
    if not config:
        # 创建默认密码：123456
        default_config = schemas.SiteConfigCreate(
            config_key="homepage_password",
            config_value="123456",
            description="首页访问密码"
        )
        create_site_config(db, default_config)
        return "123456"
    return None 