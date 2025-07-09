#!/usr/bin/env python3
"""
测试contact字段是否正确返回
"""

import requests
import json

# 测试配置
BASE_URL = "http://localhost:8000"

def test_cars_api():
    """测试车辆列表API是否包含contact字段"""
    print("测试车辆列表API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/cars")
        if response.status_code == 200:
            data = response.json()
            cars = data.get("cars", [])
            
            if cars:
                # 检查第一辆车是否包含contact字段
                first_car = cars[0]
                required_fields = ["id", "region", "image_base64", "contact", "description", "created_at"]
                missing_fields = []
                
                for field in required_fields:
                    if field not in first_car:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"❌ 缺少字段: {missing_fields}")
                    return False
                else:
                    print("✅ 所有必需字段都存在")
                    print(f"   联系方式: {first_car.get('contact', 'N/A')}")
                    return True
            else:
                print("⚠️  没有车辆数据，无法测试")
                return True
        else:
            print(f"❌ API请求失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return False

def test_car_details_api():
    """测试车辆详情API"""
    print("\n测试车辆详情API...")
    
    try:
        # 先获取车辆列表，找到一个车辆ID
        response = requests.get(f"{BASE_URL}/api/cars")
        if response.status_code == 200:
            data = response.json()
            cars = data.get("cars", [])
            
            if cars:
                car_id = cars[0]["id"]
                print(f"测试车辆ID: {car_id}")
                
                # 获取车辆详情
                detail_response = requests.get(f"{BASE_URL}/api/cars/{car_id}/details")
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    
                    if "contact" in detail_data:
                        print("✅ 车辆详情包含contact字段")
                        print(f"   联系方式: {detail_data.get('contact', 'N/A')}")
                        return True
                    else:
                        print("❌ 车辆详情缺少contact字段")
                        return False
                else:
                    print(f"❌ 获取车辆详情失败，状态码: {detail_response.status_code}")
                    return False
            else:
                print("⚠️  没有车辆数据，跳过详情测试")
                return True
        else:
            print(f"❌ 获取车辆列表失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试车辆详情出错: {e}")
        return False

if __name__ == "__main__":
    print("🔍 开始测试contact字段...")
    print(f"服务器地址: {BASE_URL}")
    
    # 测试车辆列表
    list_test_passed = test_cars_api()
    
    # 测试车辆详情
    detail_test_passed = test_car_details_api()
    
    print("\n" + "="*50)
    if list_test_passed and detail_test_passed:
        print("🎉 所有测试通过！contact字段已正确修复。")
    else:
        print("❌ 部分测试失败，请检查后端代码。")
    print("="*50) 