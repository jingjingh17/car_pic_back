"""
数据库迁移脚本：添加存储相关字段
运行此脚本来更新现有数据库结构
"""

from sqlalchemy import create_engine, text
from config import settings
import sys

def migrate_database():
    """执行数据库迁移"""
    engine = create_engine(settings.database_url)
    
    try:
        with engine.connect() as conn:
            # 开始事务
            trans = conn.begin()
            
            try:
                # 检查字段是否已存在
                result = conn.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.columns 
                    WHERE table_name = 'cars' 
                    AND column_name = 'image_key'
                    AND table_schema = DATABASE()
                """))
                
                if result.fetchone()[0] == 0:
                    print("添加 image_key 字段...")
                    conn.execute(text("""
                        ALTER TABLE cars 
                        ADD COLUMN image_key VARCHAR(255) NOT NULL DEFAULT ''
                    """))
                else:
                    print("image_key 字段已存在")
                
                # 检查 storage_type 字段
                result = conn.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.columns 
                    WHERE table_name = 'cars' 
                    AND column_name = 'storage_type'
                    AND table_schema = DATABASE()
                """))
                
                if result.fetchone()[0] == 0:
                    print("添加 storage_type 字段...")
                    conn.execute(text("""
                        ALTER TABLE cars 
                        ADD COLUMN storage_type VARCHAR(20) NOT NULL DEFAULT 'local'
                    """))
                else:
                    print("storage_type 字段已存在")
                
                # 更新现有记录的 image_key 字段
                print("更新现有记录的 image_key 字段...")
                conn.execute(text("""
                    UPDATE cars 
                    SET image_key = image_path 
                    WHERE image_key = '' OR image_key IS NULL
                """))
                
                # 提交事务
                trans.commit()
                print("数据库迁移完成！")
                
            except Exception as e:
                # 回滚事务
                trans.rollback()
                print(f"迁移失败，已回滚: {e}")
                return False
                
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("开始数据库迁移...")
    print(f"数据库URL: {settings.database_url}")
    
    if migrate_database():
        print("迁移成功完成！")
        sys.exit(0)
    else:
        print("迁移失败！")
        sys.exit(1) 