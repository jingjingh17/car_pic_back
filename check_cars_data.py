#!/usr/bin/env python3
"""
检查车辆数据脚本
查看数据库中的车辆记录情况
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

def check_cars_data():
    """检查车辆数据"""
    db = SessionLocal()
    try:
        # 获取所有车辆记录
        all_cars = db.query(models.Car).all()
        
        logger.info(f"数据库中共有 {len(all_cars)} 条车辆记录")
        
        if all_cars:
            for car in all_cars:
                logger.info(f"车辆ID: {car.id}")
                logger.info(f"  区域: {car.region}")
                logger.info(f"  联系方式: {car.contact}")
                logger.info(f"  描述: {car.description}")
                logger.info(f"  创建时间: {car.created_at}")
                logger.info(f"  有原始图片: {'是' if car.image_base64 else '否'}")
                logger.info(f"  有缩略图: {'是' if car.thumbnail_base64 else '否'}")
                
                if car.image_base64:
                    # 计算原始图片大小
                    image_size = len(car.image_base64) / 1024  # KB
                    logger.info(f"  原始图片大小: {image_size:.2f}KB")
                
                if car.thumbnail_base64:
                    # 计算缩略图大小
                    thumbnail_size = len(car.thumbnail_base64) / 1024  # KB
                    logger.info(f"  缩略图大小: {thumbnail_size:.2f}KB")
                
                logger.info("-" * 40)
        else:
            logger.info("数据库中没有车辆记录")
            
    except Exception as e:
        logger.error(f"检查车辆数据失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("开始检查车辆数据")
    check_cars_data()
    logger.info("检查完成") 