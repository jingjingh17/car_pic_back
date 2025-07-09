#!/usr/bin/env python3
"""
检查缩略图字段脚本
专门检查缩略图字段的情况
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal
import models
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_thumbnail_field():
    """检查缩略图字段"""
    db = SessionLocal()
    try:
        # 获取所有车辆记录
        all_cars = db.query(models.Car).all()
        
        logger.info(f"数据库中共有 {len(all_cars)} 条车辆记录")
        
        if all_cars:
            for car in all_cars:
                logger.info(f"车辆ID: {car.id}")
                
                # 检查缩略图字段
                if car.thumbnail_base64 is None:
                    logger.info("  缩略图字段: NULL")
                elif car.thumbnail_base64 == "":
                    logger.info("  缩略图字段: 空字符串")
                else:
                    logger.info("  缩略图字段: 有数据")
                    logger.info(f"  缩略图长度: {len(car.thumbnail_base64)} 字符")
                    logger.info(f"  缩略图大小: {len(car.thumbnail_base64) / 1024:.2f}KB")
                    
                    # 检查是否是有效的base64图片
                    if car.thumbnail_base64.startswith('data:image/'):
                        logger.info("  缩略图格式: 有效的base64图片")
                    else:
                        logger.info("  缩略图格式: 无效的base64图片")
                
                logger.info("-" * 40)
        else:
            logger.info("数据库中没有车辆记录")
            
    except Exception as e:
        logger.error(f"检查缩略图字段失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("开始检查缩略图字段")
    check_thumbnail_field()
    logger.info("检查完成") 