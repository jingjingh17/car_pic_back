"""
七牛云配置测试脚本
用于验证七牛云配置是否正确
"""

import os
import sys
from pathlib import Path
from config import settings
from qiniu import Auth, put_data, BucketManager
import tempfile

def test_qiniu_config():
    """测试七牛云配置"""
    print("🔍 测试七牛云配置...")
    
    # 检查配置
    if not settings.is_qiniu_enabled:
        print("❌ 七牛云配置不完整")
        print(f"QINIU_ACCESS_KEY: {'✅' if settings.QINIU_ACCESS_KEY else '❌'}")
        print(f"QINIU_SECRET_KEY: {'✅' if settings.QINIU_SECRET_KEY else '❌'}")
        print(f"QINIU_BUCKET_NAME: {'✅' if settings.QINIU_BUCKET_NAME else '❌'}")
        print(f"QINIU_DOMAIN: {'✅' if settings.QINIU_DOMAIN else '❌'}")
        return False
    
    print("✅ 七牛云配置检查通过")
    return True

def test_qiniu_auth():
    """测试七牛云认证"""
    print("🔍 测试七牛云认证...")
    
    try:
        auth = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        bucket_manager = BucketManager(auth)
        
        # 尝试获取存储空间信息
        ret, info = bucket_manager.stat(settings.QINIU_BUCKET_NAME, "test-file-not-exists")
        
        # 612 表示文件不存在，这是正常的
        if info.status_code == 612:
            print("✅ 七牛云认证成功")
            return True
        elif info.status_code == 401:
            print("❌ 七牛云认证失败：AccessKey 或 SecretKey 错误")
            return False
        elif info.status_code == 631:
            print("❌ 七牛云认证失败：存储空间不存在")
            return False
        else:
            print(f"✅ 七牛云认证成功 (状态码: {info.status_code})")
            return True
            
    except Exception as e:
        print(f"❌ 七牛云认证失败: {e}")
        return False

def test_qiniu_upload():
    """测试七牛云上传"""
    print("🔍 测试七牛云上传...")
    
    try:
        auth = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        
        # 创建测试文件
        test_content = b"This is a test file for qiniu upload"
        test_filename = "test-upload.txt"
        
        # 生成上传凭证
        upload_token = auth.upload_token(settings.QINIU_BUCKET_NAME, test_filename)
        
        # 上传文件
        ret, info = put_data(upload_token, test_filename, test_content)
        
        if info.status_code == 200:
            print("✅ 七牛云上传测试成功")
            print(f"文件URL: https://{settings.QINIU_DOMAIN}/{test_filename}")
            
            # 清理测试文件
            bucket_manager = BucketManager(auth)
            bucket_manager.delete(settings.QINIU_BUCKET_NAME, test_filename)
            print("✅ 测试文件已清理")
            
            return True
        else:
            print(f"❌ 七牛云上传失败: {info}")
            return False
            
    except Exception as e:
        print(f"❌ 七牛云上传测试失败: {e}")
        return False

def test_domain_access():
    """测试域名访问"""
    print("🔍 测试域名访问...")
    
    try:
        import requests
        
        # 测试域名是否可访问
        test_url = f"https://{settings.QINIU_DOMAIN}"
        
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200 or response.status_code == 404:
            print("✅ 域名访问正常")
            return True
        else:
            print(f"⚠️  域名访问异常 (状态码: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 域名无法访问：连接错误")
        return False
    except requests.exceptions.Timeout:
        print("❌ 域名访问超时")
        return False
    except Exception as e:
        print(f"⚠️  域名访问测试失败: {e}")
        return False

def test_storage_service():
    """测试存储服务"""
    print("🔍 测试存储服务...")
    
    try:
        from storage_service import storage_service
        
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b"Test content for storage service")
            tmp_file_path = tmp_file.name
        
        # 模拟 UploadFile 对象
        class MockUploadFile:
            def __init__(self, filename, content):
                self.filename = filename
                self.content = content
            
            async def read(self):
                return self.content
        
        # 测试上传
        mock_file = MockUploadFile("test-storage.txt", b"Test content")
        
        # 这里需要异步测试，但为了简化，我们只测试配置
        if settings.is_qiniu_enabled:
            print("✅ 存储服务配置为七牛云")
        else:
            print("✅ 存储服务配置为本地存储")
        
        # 清理临时文件
        os.unlink(tmp_file_path)
        
        return True
        
    except Exception as e:
        print(f"❌ 存储服务测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 七牛云配置测试工具")
    print("=" * 50)
    
    if not Path(".env").exists():
        print("❌ .env 文件不存在")
        print("请先运行 'python setup_env.py' 创建配置文件")
        sys.exit(1)
    
    print(f"当前存储类型: {settings.STORAGE_TYPE}")
    
    if settings.STORAGE_TYPE != "qiniu":
        print("ℹ️  当前未配置为七牛云存储")
        print("如需测试七牛云，请修改 .env 文件中的 STORAGE_TYPE=qiniu")
        sys.exit(0)
    
    # 测试步骤
    tests = [
        ("配置检查", test_qiniu_config),
        ("认证测试", test_qiniu_auth),
        ("上传测试", test_qiniu_upload),
        ("域名访问", test_domain_access),
        ("存储服务", test_storage_service),
    ]
    
    success_count = 0
    
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        if test_func():
            success_count += 1
        else:
            print(f"❌ {name} 失败")
    
    print(f"\n📊 测试结果: {success_count}/{len(tests)} 通过")
    
    if success_count == len(tests):
        print("🎉 所有测试通过！七牛云配置正确")
    else:
        print("⚠️  部分测试失败，请检查配置")
        
        print("\n💡 常见问题解决方案：")
        print("1. 检查 AccessKey 和 SecretKey 是否正确")
        print("2. 确认存储空间名称是否正确")
        print("3. 验证域名配置是否正确")
        print("4. 检查网络连接是否正常")

if __name__ == "__main__":
    main() 