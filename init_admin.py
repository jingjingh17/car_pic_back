#!/usr/bin/env python3
"""
数据库初始化脚本 - 创建默认管理员用户
"""

import os
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models
import crud
import schemas

def init_database():
    """初始化数据库，创建表和默认管理员用户"""
    
    # 创建所有表
    models.Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建完成")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已存在管理员用户
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        existing_user = crud.get_user_by_username(db, admin_username)
        
        if existing_user:
            print(f"✓ 管理员用户 '{admin_username}' 已存在")
        else:
            # 创建默认管理员用户
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            admin_user = schemas.UserCreate(
                username=admin_username,
                password=admin_password
            )
            
            crud.create_user(db, admin_user)
            print(f"✓ 默认管理员用户创建成功")
            print(f"  用户名: {admin_username}")
            print(f"  密码: {admin_password}")
            print("  请在生产环境中修改默认密码！")
            
    except Exception as e:
        print(f"✗ 创建管理员用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 初始化数据库...")
    print("=" * 50)
    init_database()
    print("=" * 50)
    print("🎉 数据库初始化完成！") 