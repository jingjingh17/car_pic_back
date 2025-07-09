#!/usr/bin/env python3
"""
测试BASE64存储系统
"""

import os
import sys
import base64
import requests
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_base64_storage():
    """测试BASE64存储功能"""
    print("测试BASE64存储系统...")
    
    base_url = "http://localhost:8000"
    
    # 1. 测试系统配置
    print("1. 测试系统配置...")
    try:
        response = requests.get(f"{base_url}/api/config")
        if response.status_code == 200:
            config = response.json()
            print(f"   ✓ 存储类型: {config.get('storage_type')}")
            print(f"   ✓ 最大文件大小: {config.get('max_file_size')}")
        else:
            print(f"   ✗ 配置获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ 配置获取错误: {e}")
        return False
    
    # 2. 测试获取车辆列表
    print("2. 测试获取车辆列表...")
    try:
        response = requests.get(f"{base_url}/api/cars")
        if response.status_code == 200:
            cars_data = response.json()
            cars = cars_data.get('cars', [])
            print(f"   ✓ 找到 {len(cars)} 辆车")
            
            # 检查第一辆车的数据结构
            if cars:
                car = cars[0]
                print(f"   ✓ 车辆ID: {car.get('id')}")
                print(f"   ✓ 区域: {car.get('region')}")
                
                # 检查BASE64数据
                image_base64 = car.get('image_base64')
                if image_base64:
                    if image_base64.startswith('data:image/'):
                        print(f"   ✓ BASE64图片数据有效 (长度: {len(image_base64)})")
                    else:
                        print(f"   ✗ BASE64图片数据格式无效")
                else:
                    print(f"   ✗ 缺少BASE64图片数据")
        else:
            print(f"   ✗ 车辆列表获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ 车辆列表获取错误: {e}")
        return False
    
    # 3. 测试图片验证API
    print("3. 测试图片验证API...")
    try:
        # 创建一个测试图片文件
        test_image_path = "test_image.jpg"
        
        # 创建一个简单的测试图片数据（1x1像素的JPEG）
        test_image_data = base64.b64decode(
            "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/8A"
        )
        
        with open(test_image_path, 'wb') as f:
            f.write(test_image_data)
        
        # 测试图片验证
        with open(test_image_path, 'rb') as f:
            files = {'image': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{base_url}/api/validate-image", files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('is_valid'):
                    print(f"   ✓ 图片验证成功: {result.get('mime_type')}")
                else:
                    print(f"   ✗ 图片验证失败: {result.get('error')}")
            else:
                print(f"   ✗ 图片验证API失败: {response.status_code}")
        
        # 清理测试文件
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            
    except Exception as e:
        print(f"   ✗ 图片验证测试错误: {e}")
        # 清理测试文件
        if os.path.exists("test_image.jpg"):
            os.remove("test_image.jpg")
    
    print("\n✓ BASE64存储系统测试完成!")
    return True

if __name__ == "__main__":
    print("请确保后端服务器正在运行 (python main.py)")
    input("按回车键开始测试...")
    test_base64_storage() 