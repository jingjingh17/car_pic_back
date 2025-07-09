#!/usr/bin/env python3
"""
批量生成缩略图脚本
为现有车辆记录生成缩略图
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal
import models
from storage_service import storage_service
import base64
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_thumbnails_for_existing_cars():
    """为现有车辆记录生成缩略图"""
    db = SessionLocal()
    try:
        # 获取所有没有缩略图的车辆记录
        cars_without_thumbnails = db.query(models.Car).filter(
            models.Car.thumbnail_base64.is_(None)
        ).all()
        
        logger.info(f"找到 {len(cars_without_thumbnails)} 条需要生成缩略图的记录")
        
        success_count = 0
        error_count = 0
        
        for car in cars_without_thumbnails:
            try:
                logger.info(f"正在为车辆 {car.id} 生成缩略图...")
                
                # 检查是否有原始图片数据
                if not car.image_base64:
                    logger.warning(f"车辆 {car.id} 没有原始图片数据，跳过")
                    error_count += 1
                    continue
                
                # 提取原始图片数据
                if ';base64,' in car.image_base64:
                    image_data = base64.b64decode(car.image_base64.split(';base64,')[1])
                    mime_type = car.image_base64.split(';')[0].replace('data:', '')
                    
                    # 生成缩略图
                    thumbnail_data = await storage_service.create_thumbnail(image_data, mime_type)
                    
                    if thumbnail_data:
                        # 更新数据库
                        car.thumbnail_base64 = thumbnail_data
                        db.commit()
                        success_count += 1
                        logger.info(f"✓ 车辆 {car.id} 缩略图生成成功")
                    else:
                        error_count += 1
                        logger.error(f"✗ 车辆 {car.id} 缩略图生成失败")
                else:
                    error_count += 1
                    logger.error(f"✗ 车辆 {car.id} 图片数据格式错误")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"✗ 车辆 {car.id} 处理失败: {e}")
                db.rollback()
        
        logger.info(f"缩略图生成完成: 成功 {success_count} 条，失败 {error_count} 条")
        
    except Exception as e:
        logger.error(f"批量生成缩略图失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import asyncio
    logger.info("开始批量生成缩略图")
    asyncio.run(generate_thumbnails_for_existing_cars())
    logger.info("批量生成缩略图完成") 