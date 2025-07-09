"""
环境配置设置脚本
用于创建 .env 文件和配置存储类型
"""

import os
from pathlib import Path

def create_env_file():
    """创建 .env 文件"""
    env_content = """# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=car_management
DB_USER=root
DB_PASSWORD=your_password

# JWT配置
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 文件存储配置
STORAGE_TYPE=qiniu  # local 或 qiniu
UPLOAD_DIR=uploads

# 七牛云配置
QINIU_ACCESS_KEY=AfdmRc7F433HD1pfW49G5FNnCN1YXubrXOjlc-kq
QINIU_SECRET_KEY=kkptjXEMYFJIzBTZUhzF-OhPNtf4aVnsQwfmDeJz
QINIU_BUCKET_NAME=custom-carpic
QINIU_DOMAIN=sj6q8wy5a.hn-bkt.clouddn.com

# 服务器配置
HOST=0.0.0.0
PORT=8000
"""
    
    env_path = Path(".env")
    
    if env_path.exists():
        print("⚠️  .env 文件已存在")
        choice = input("是否覆盖现有文件？(y/n): ").lower()
        if choice != 'y':
            print("取消操作")
            return False
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ .env 文件创建成功！")
    print("\n📝 请根据需要修改以下配置：")
    print("1. 数据库连接信息 (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)")
    print("2. JWT密钥 (SECRET_KEY)")
    print("3. 存储类型 (STORAGE_TYPE: local 或 qiniu)")
    print("4. 七牛云配置 (如果使用七牛云存储)")
    
    return True

def switch_storage_type():
    """切换存储类型"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env 文件不存在，请先创建")
        return False
    
    print("\n当前支持的存储类型：")
    print("1. local - 本地存储")
    print("2. qiniu - 七牛云存储")
    
    choice = input("\n请选择存储类型 (1/2): ").strip()
    
    if choice == "1":
        storage_type = "local"
    elif choice == "2":
        storage_type = "qiniu"
    else:
        print("❌ 无效选择")
        return False
    
    # 读取现有配置
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新存储类型
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('STORAGE_TYPE='):
            lines[i] = f'STORAGE_TYPE={storage_type}'
            break
    
    # 写回文件
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ 存储类型已切换为: {storage_type}")
    
    if storage_type == "qiniu":
        print("\n📋 使用七牛云存储需要确保以下配置正确：")
        print("- QINIU_ACCESS_KEY")
        print("- QINIU_SECRET_KEY")
        print("- QINIU_BUCKET_NAME")
        print("- QINIU_DOMAIN")
    
    return True

def main():
    """主函数"""
    print("🚀 车辆图片管理系统 - 环境配置工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作：")
        print("1. 创建 .env 文件")
        print("2. 切换存储类型")
        print("3. 查看当前配置")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == "1":
            create_env_file()
        elif choice == "2":
            switch_storage_type()
        elif choice == "3":
            show_current_config()
        elif choice == "4":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重新输入")

def show_current_config():
    """显示当前配置"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env 文件不存在")
        return
    
    print("\n📋 当前配置：")
    print("-" * 30)
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if 'PASSWORD' in line or 'SECRET' in line or 'KEY' in line:
                    # 隐藏敏感信息
                    key, value = line.split('=', 1)
                    print(f"{key}=***")
                else:
                    print(line)

if __name__ == "__main__":
    main() 