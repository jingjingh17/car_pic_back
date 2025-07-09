#!/usr/bin/env python3
"""
车辆图片管理系统后端启动脚本
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import mysql.connector
        print("✓ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_database():
    """检查数据库连接"""
    try:
        from database import engine
        with engine.connect() as conn:
            print("✓ 数据库连接成功")
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        print("请确保MySQL服务已启动，并创建了pic_db数据库")
        return False

def init_database():
    """初始化数据库和管理员用户"""
    try:
        from init_admin import init_database
        init_database()
        return True
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        return False

def create_upload_directory():
    """创建上传目录"""
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    print("✓ 上传目录已创建")

def main():
    print("🚗 车辆图片管理系统后端启动中...")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 创建上传目录
    create_upload_directory()
    
    # 检查数据库连接
    if not check_database():
        print("\n数据库配置说明:")
        print("1. 确保MySQL服务已启动")
        print("2. 创建数据库: CREATE DATABASE pic_db;")
        print("3. 在.env文件中配置数据库连接信息")
        sys.exit(1)
    
    # 初始化数据库和管理员用户
    if not init_database():
        print("\n数据库初始化失败，但服务器仍会启动")
        print("请检查数据库配置或手动运行 python init_admin.py")
    
    print("\n✓ 所有检查通过，启动服务器...")
    print("🌐 服务器地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("=" * 50)
    
    # 启动服务器 - 根据环境判断是否使用reload
    import uvicorn
    
    # 检查是否在生产环境（Railway会设置这个环境变量）
    is_production = os.getenv("RAILWAY_ENVIRONMENT") is not None or os.getenv("PORT") is not None
    port = int(os.getenv("PORT", 8000))
    
    if is_production:
        # 生产环境配置
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port
        )
    else:
        # 开发环境配置
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            reload_dirs=["./"]
        )

if __name__ == "__main__":
    main() 