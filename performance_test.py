#!/usr/bin/env python3
"""
性能测试脚本
测试优化前后的API响应时间
"""

import requests
import time
import json
from datetime import datetime

# API基础URL
BASE_URL = "https://carpicback-production.up.railway.app"

def test_api_performance():
    """测试API性能"""
    print("=" * 60)
    print("车辆图片管理系统 - API性能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {BASE_URL}")
    print()
    
    # 测试1: 获取车辆列表（优化前 - 包含图片数据）
    print("测试1: 获取车辆列表（包含图片数据）")
    print("-" * 40)
    
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/api/cars?page=1&limit=5", timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            response_size = len(response.content)
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            print(f"✓ 请求成功")
            print(f"  响应时间: {response_time:.2f}ms")
            print(f"  响应大小: {response_size / 1024:.2f}KB")
            print(f"  车辆数量: {len(data.get('cars', []))}")
            
            # 检查是否包含图片数据
            has_images = any('image_base64' in car for car in data.get('cars', []))
            print(f"  包含图片数据: {'是' if has_images else '否'}")
            
        else:
            print(f"✗ 请求失败: {response.status_code}")
            print(f"  错误信息: {response.text}")
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
    
    print()
    
    # 测试2: 获取单个车辆缩略图
    print("测试2: 获取单个车辆缩略图")
    print("-" * 40)
    
    try:
        # 先获取车辆列表
        cars_response = requests.get(f"{BASE_URL}/api/cars?page=1&limit=1", timeout=10)
        if cars_response.status_code == 200:
            cars_data = cars_response.json()
            if cars_data.get('cars'):
                car_id = cars_data['cars'][0]['id']
                
                start_time = time.time()
                thumbnail_response = requests.get(f"{BASE_URL}/api/cars/{car_id}/thumbnail", timeout=30)
                end_time = time.time()
                
                if thumbnail_response.status_code == 200:
                    thumbnail_data = thumbnail_response.json()
                    response_size = len(thumbnail_response.content)
                    response_time = (end_time - start_time) * 1000
                    
                    print(f"✓ 缩略图请求成功")
                    print(f"  车辆ID: {car_id}")
                    print(f"  响应时间: {response_time:.2f}ms")
                    print(f"  响应大小: {response_size / 1024:.2f}KB")
                    print(f"  有缩略图: {'是' if thumbnail_data.get('thumbnail_base64') else '否'}")
                    
                else:
                    print(f"✗ 缩略图请求失败: {thumbnail_response.status_code}")
            else:
                print("✗ 没有找到车辆数据")
        else:
            print(f"✗ 获取车辆列表失败: {cars_response.status_code}")
            
    except Exception as e:
        print(f"✗ 缩略图请求异常: {e}")
    
    print()
    
    # 测试3: 并发请求测试
    print("测试3: 并发请求测试（5个并发）")
    print("-" * 40)
    
    import concurrent.futures
    
    def make_request():
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/api/cars?page=1&limit=1", timeout=10)
            end_time = time.time()
            return {
                'success': response.status_code == 200,
                'time': (end_time - start_time) * 1000,
                'size': len(response.content)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'time': 0,
                'size': 0
            }
    
    try:
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in futures]
        end_time = time.time()
        
        total_time = (end_time - start_time) * 1000
        success_count = sum(1 for r in results if r['success'])
        avg_time = sum(r['time'] for r in results if r['success']) / success_count if success_count > 0 else 0
        
        print(f"✓ 并发测试完成")
        print(f"  总时间: {total_time:.2f}ms")
        print(f"  成功请求: {success_count}/5")
        print(f"  平均响应时间: {avg_time:.2f}ms")
        
    except Exception as e:
        print(f"✗ 并发测试异常: {e}")
    
    print()
    print("=" * 60)
    print("性能测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_api_performance() 