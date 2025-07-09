#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加site_config表并初始化首页密码
"""

import os
import sys
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models
import crud
import schemas

def run_migration():
    """运行数据库迁移"""
    
    print("开始数据库迁移...")
    
    # 创建所有表（包括新的site_config表）
    models.Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建/更新完成")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 初始化默认首页密码
        default_password = crud.init_default_homepage_password(db)
        if default_password:
            print(f"✓ 默认首页密码已设置: {default_password}")
            print("  管理员可以在后台修改此密码")
        else:
            print("✓ 首页密码配置已存在，跳过初始化")
            
    except Exception as e:
        print(f"✗ 迁移过程中出现错误: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    print("✓ 数据库迁移完成！")
    return True

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("\n迁移成功！现在可以启动应用程序。")
        print("默认首页密码: 123456")
        print("管理员可以在后台管理界面修改此密码。")
        sys.exit(0)
    else:
        print("\n迁移失败！请检查错误信息。")
        sys.exit(1) 