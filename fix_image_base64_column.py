#!/usr/bin/env python3
"""
修复image_base64字段类型为LONGTEXT
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_image_base64_column():
    """修复image_base64字段类型"""
    print("开始修复image_base64字段类型...")
    
    # 创建数据库连接
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        try:
            # 检查当前字段类型
            print("1. 检查当前字段类型...")
            result = db.execute(text("""
                SELECT COLUMN_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :db_name 
                AND TABLE_NAME = 'cars' 
                AND COLUMN_NAME = 'image_base64'
            """), {"db_name": settings.DB_NAME})
            
            current_type = result.fetchone()
            if current_type:
                print(f"   当前字段类型: {current_type[0]}")
                
                if current_type[0].lower() == 'longtext':
                    print("   ✓ 字段类型已经是LONGTEXT，无需修改")
                    return True
            else:
                print("   ✗ 未找到image_base64字段")
                return False
            
            # 修改字段类型
            print("2. 修改字段类型为LONGTEXT...")
            db.execute(text("ALTER TABLE cars MODIFY COLUMN image_base64 LONGTEXT NOT NULL"))
            db.commit()
            print("   ✓ 字段类型修改成功")
            
            # 验证修改结果
            print("3. 验证修改结果...")
            result = db.execute(text("""
                SELECT COLUMN_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :db_name 
                AND TABLE_NAME = 'cars' 
                AND COLUMN_NAME = 'image_base64'
            """), {"db_name": settings.DB_NAME})
            
            new_type = result.fetchone()
            if new_type:
                print(f"   新字段类型: {new_type[0]}")
                if new_type[0].lower() == 'longtext':
                    print("   ✓ 字段类型修改验证成功")
                else:
                    print("   ✗ 字段类型修改验证失败")
                    return False
            
        except Exception as e:
            db.rollback()
            print(f"修复失败: {e}")
            return False
    
    print("\n✓ image_base64字段类型修复完成!")
    return True

if __name__ == "__main__":
    fix_image_base64_column() 