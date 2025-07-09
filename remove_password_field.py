#!/usr/bin/env python3
"""
删除cars表中的password字段
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

def remove_password_field():
    """删除cars表中的password字段"""
    try:
        # 创建数据库连接
        engine = create_engine(settings.database_url)
        
        with engine.connect() as db:
            # 检查password字段是否存在
            result = db.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'cars' 
                AND COLUMN_NAME = 'password'
            """))
            
            if result.fetchone():
                logger.info("发现password字段，正在删除...")
                
                # 删除password字段
                db.execute(text("ALTER TABLE cars DROP COLUMN password"))
                
                logger.info("✓ password字段删除成功")
            else:
                logger.info("✓ password字段不存在，无需删除")
            
    except Exception as e:
        logger.error(f"删除password字段失败: {e}")
        raise

if __name__ == "__main__":
    logger.info("开始删除cars表中的password字段")
    remove_password_field()
    logger.info("删除完成") 