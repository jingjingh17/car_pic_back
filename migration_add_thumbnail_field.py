#!/usr/bin/env python3
"""
数据库迁移脚本：添加缩略图字段
为cars表添加thumbnail_base64字段，用于存储压缩后的缩略图数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from config import settings
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_thumbnail_field():
    """添加缩略图字段到cars表"""
    try:
        # 创建数据库连接
        engine = create_engine(settings.database_url)
        
        with engine.connect() as db:
            # 检查字段是否已存在
            result = db.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'cars' 
                AND COLUMN_NAME = 'thumbnail_base64'
            """))
            
            if result.fetchone():
                logger.info("✓ thumbnail_base64字段已存在，跳过添加")
                return
            
            # 添加缩略图字段
            logger.info("正在添加thumbnail_base64字段...")
            db.execute(text("""
                ALTER TABLE cars 
                ADD COLUMN thumbnail_base64 LONGTEXT NULL 
                COMMENT '缩略图数据，用于快速加载'
            """))
            
            logger.info("✓ thumbnail_base64字段添加成功")
            
            # 为现有记录生成缩略图（可选，这里先跳过）
            logger.info("注意：现有记录的缩略图字段为空，将在下次更新时自动生成")
            
    except Exception as e:
        logger.error(f"添加缩略图字段失败: {e}")
        raise

if __name__ == "__main__":
    logger.info("开始执行数据库迁移：添加缩略图字段")
    add_thumbnail_field()
    logger.info("数据库迁移完成") 