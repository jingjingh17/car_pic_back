import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings:
    # 数据库配置
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_NAME: str = os.getenv("DB_NAME", "pic_db")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # 文件存储配置
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # local 或 qiniu
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    
    # 七牛云配置
    QINIU_ACCESS_KEY: str = os.getenv("QINIU_ACCESS_KEY", "")
    QINIU_SECRET_KEY: str = os.getenv("QINIU_SECRET_KEY", "")
    QINIU_BUCKET_NAME: str = os.getenv("QINIU_BUCKET_NAME", "")
    QINIU_DOMAIN: str = os.getenv("QINIU_DOMAIN", "")
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    @property
    def database_url(self) -> str:
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def is_qiniu_enabled(self) -> bool:
        return (self.STORAGE_TYPE == "qiniu" and 
                self.QINIU_ACCESS_KEY and 
                self.QINIU_SECRET_KEY and 
                self.QINIU_BUCKET_NAME)

# 创建全局设置实例
settings = Settings() 