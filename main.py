from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from database import get_db, engine
import models
import schemas
import crud
from config import settings
from storage_service import storage_service

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="车辆图片管理系统", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT配置
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效的认证令牌")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的认证令牌")

@app.get("/")
async def root():
    return {
        "message": "车辆图片管理系统API",
        "storage_type": "base64"
    }

@app.get("/api/config")
async def get_config():
    """获取系统配置信息"""
    return {
        "storage_type": "base64",
        "max_file_size": "5MB"
    }

@app.post("/api/admin/login")
async def admin_login(login_data: schemas.AdminLogin, db: Session = Depends(get_db)):
    """管理员登录"""
    # 从数据库验证用户
    user = crud.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/admin/create-user")
async def create_admin_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: str = Depends(verify_token)):
    """创建新的管理员用户（需要已登录的管理员权限）"""
    # 检查用户名是否已存在
    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建新用户
    new_user = crud.create_user(db, user)
    return {"message": f"用户 '{new_user.username}' 创建成功", "user_id": new_user.id}

@app.get("/api/regions")
async def get_regions():
    """获取所有区域"""
    regions = ["福田", "罗湖", "南山", "龙华", "龙岗", "宝安", "沙井", "广州"]
    return {"regions": regions}

@app.get("/api/cars")
async def get_cars(region: str = None, db: Session = Depends(get_db)):
    """获取车辆列表"""
    return crud.get_cars(db, region=region)

@app.post("/api/cars")
async def create_car(
    region: str = Form(...),
    password: str = Form(...),
    contact: str = Form(...),
    description: str = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """创建新车辆记录"""
    return await crud.create_car(db, region, password, contact, description, image)

@app.post("/api/cars/{car_id}/verify")
async def verify_password(car_id: int, password_data: schemas.PasswordVerify, db: Session = Depends(get_db)):
    """验证密码"""
    return crud.verify_car_password(db, car_id, password_data.password)

@app.get("/api/cars/{car_id}/details")
async def get_car_details(car_id: int, db: Session = Depends(get_db)):
    """获取车辆详情（需要先验证密码）"""
    return crud.get_car_details(db, car_id)

@app.delete("/api/cars/{car_id}")
async def delete_car(car_id: int, db: Session = Depends(get_db), current_user: str = Depends(verify_token)):
    """删除车辆（需要管理员权限）"""
    return await crud.delete_car(db, car_id)

@app.put("/api/cars/{car_id}")
async def update_car(
    car_id: int,
    region: str = Form(None),
    password: str = Form(None),
    contact: str = Form(None),
    description: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """更新车辆信息（需要管理员权限）"""
    return await crud.update_car(db, car_id, region, password, contact, description, image)

@app.get("/api/cars/{car_id}/image")
async def get_car_image(car_id: int, db: Session = Depends(get_db)):
    """获取车辆图片的BASE64数据"""
    car = crud.get_car_by_id(db, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="车辆不存在")
    
    return {
        "car_id": car_id,
        "image_base64": car.image_base64,
        "message": "图片数据获取成功"
    }

@app.post("/api/validate-image")
async def validate_image(image: UploadFile = File(...)):
    """验证上传的图片是否有效"""
    try:
        upload_result = await storage_service.upload_file(image)
        image_info = storage_service.get_image_info(upload_result["base64_data"])
        
        return {
            "is_valid": True,
            "mime_type": image_info["mime_type"],
            "size": image_info["size"],
            "message": "图片验证成功"
        }
    except HTTPException as e:
        return {
            "is_valid": False,
            "error": str(e.detail),
            "message": "图片验证失败"
        }

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=True) 