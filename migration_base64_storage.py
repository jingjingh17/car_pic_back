#!/usr/bin/env python3
"""
数据库迁移脚本：将文件存储迁移到BASE64存储
"""

import os
import sys
import base64
import mimetypes
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_file_mime_type(file_path):
    """获取文件的MIME类型"""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith('image/'):
        return mime_type
    return 'image/jpeg'  # 默认为JPEG

def file_to_base64(file_path):
    """将文件转换为BASE64格式"""
    try:
        if not os.path.exists(file_path):
            print(f"警告: 文件不存在 {file_path}")
            return None
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        mime_type = get_file_mime_type(file_path)
        base64_data = base64.b64encode(content).decode('utf-8')
        data_url = f"data:{mime_type};base64,{base64_data}"
        
        return data_url
    except Exception as e:
        print(f"错误: 无法转换文件 {file_path}: {e}")
        return None

def migrate_to_base64():
    """执行迁移"""
    print("开始迁移数据库到BASE64存储...")
    
    # 创建数据库连接
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        try:
            # 1. 添加新的image_base64字段
            print("1. 添加image_base64字段...")
            try:
                db.execute(text("ALTER TABLE cars ADD COLUMN image_base64 TEXT"))
                db.commit()
                print("   ✓ image_base64字段添加成功")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e).lower():
                    print("   ✓ image_base64字段已存在")
                else:
                    raise e
            
            # 2. 获取所有需要迁移的记录
            print("2. 获取现有记录...")
            try:
                result = db.execute(text("SELECT id, image_path, image_key, storage_type FROM cars WHERE image_base64 IS NULL OR image_base64 = ''"))
                cars = result.fetchall()
                print(f"   找到 {len(cars)} 条记录需要迁移")
            except Exception as e:
                if "doesn't exist" in str(e) or "unknown column" in str(e).lower():
                    print("   ✓ 旧字段不存在，无需迁移")
                    return True
                else:
                    raise e
            
            # 3. 迁移每条记录
            success_count = 0
            error_count = 0
            
            for car in cars:
                car_id, image_path, image_key, storage_type = car
                print(f"   处理车辆ID {car_id}...")
                
                base64_data = None
                
                if storage_type == "local":
                    # 本地文件存储
                    if image_path.startswith('/'):
                        # 移除开头的斜杠
                        file_path = image_path[1:]
                    else:
                        file_path = image_path
                    
                    # 尝试不同的路径
                    possible_paths = [
                        file_path,
                        os.path.join(settings.UPLOAD_DIR, os.path.basename(file_path)),
                        image_key if image_key else None
                    ]
                    
                    for path in possible_paths:
                        if path and os.path.exists(path):
                            base64_data = file_to_base64(path)
                            if base64_data:
                                break
                
                elif storage_type == "qiniu":
                    # 七牛云存储 - 需要下载文件
                    print(f"     警告: 七牛云文件 {image_key} 需要手动处理")
                    # 这里可以添加七牛云下载逻辑
                    continue
                
                if base64_data:
                    # 更新数据库记录
                    db.execute(
                        text("UPDATE cars SET image_base64 = :base64_data WHERE id = :car_id"),
                        {"base64_data": base64_data, "car_id": car_id}
                    )
                    success_count += 1
                    print(f"     ✓ 成功迁移车辆ID {car_id}")
                else:
                    error_count += 1
                    print(f"     ✗ 无法迁移车辆ID {car_id} (文件不存在或无法读取)")
            
            # 4. 提交更改
            db.commit()
            
            print(f"\n迁移完成:")
            print(f"  成功: {success_count} 条记录")
            print(f"  失败: {error_count} 条记录")
            
            if error_count == 0:
                # 5. 删除旧字段（可选）
                print("\n5. 清理旧字段...")
                response = input("是否删除旧的存储字段 (image_path, image_key, storage_type)? [y/N]: ")
                if response.lower() == 'y':
                    try:
                        db.execute(text("ALTER TABLE cars DROP COLUMN image_path"))
                        db.execute(text("ALTER TABLE cars DROP COLUMN image_key"))
                        db.execute(text("ALTER TABLE cars DROP COLUMN storage_type"))
                        db.commit()
                        print("   ✓ 旧字段删除成功")
                    except Exception as e:
                        print(f"   ✗ 删除旧字段失败: {e}")
                        print("   提示: 可以稍后手动删除这些字段")
            
        except Exception as e:
            db.rollback()
            print(f"迁移失败: {e}")
            return False
    
    print("\n✓ 数据库迁移完成!")
    return True

def rollback_migration():
    """回滚迁移（如果需要）"""
    print("开始回滚迁移...")
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        try:
            # 删除image_base64字段
            db.execute(text("ALTER TABLE cars DROP COLUMN image_base64"))
            db.commit()
            print("✓ 回滚完成")
        except Exception as e:
            print(f"回滚失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        migrate_to_base64() 