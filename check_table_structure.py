#!/usr/bin/env python3
"""
检查数据库表结构脚本
查看cars表的字段结构
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

def check_table_structure():
    """检查cars表结构"""
    try:
        # 创建数据库连接
        engine = create_engine(settings.database_url)
        
        with engine.connect() as db:
            # 获取cars表的结构
            result = db.execute(text("""
                DESCRIBE cars
            """))
            
            logger.info("cars表结构:")
            logger.info("-" * 50)
            
            for row in result:
                field_name = row[0]
                field_type = row[1]
                field_null = row[2]
                field_key = row[3]
                field_default = row[4]
                field_extra = row[5]
                
                logger.info(f"字段名: {field_name}")
                logger.info(f"  类型: {field_type}")
                logger.info(f"  允许NULL: {field_null}")
                logger.info(f"  键类型: {field_key}")
                logger.info(f"  默认值: {field_default}")
                logger.info(f"  额外: {field_extra}")
                logger.info("-" * 30)
            
    except Exception as e:
        logger.error(f"检查表结构失败: {e}")
        raise

if __name__ == "__main__":
    logger.info("开始检查cars表结构")
    check_table_structure()
    logger.info("检查完成") 