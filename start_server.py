"""
车辆图片管理系统启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path
from config import settings

def check_dependencies():
    """检查依赖包"""
    print("🔍 检查依赖包...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'mysql-connector-python',
        'python-multipart',
        'pillow',
        'python-jose',
        'passlib',
        'python-dotenv',
        'qiniu'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少以下依赖包: {', '.join(missing_packages)}")
        print("正在安装...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages)
            print("✅ 依赖包安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖包安装失败")
            return False
    else:
        print("✅ 所有依赖包已安装")
    
    return True

def check_env_file():
    """检查环境文件"""
    print("🔍 检查环境配置...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env 文件不存在")
        print("请运行 'python setup_env.py' 创建环境配置文件")
        return False
    
    print("✅ 环境配置文件存在")
    return True

def check_database():
    """检查数据库连接"""
    print("🔍 检查数据库连接...")
    
    try:
        from database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ 数据库连接成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("请检查数据库配置和连接")
        return False

def check_storage_config():
    """检查存储配置"""
    print("🔍 检查存储配置...")
    
    print(f"存储类型: {settings.STORAGE_TYPE}")
    
    if settings.STORAGE_TYPE == "qiniu":
        if settings.is_qiniu_enabled:
            print("✅ 七牛云配置完整")
        else:
            print("❌ 七牛云配置不完整")
            print("请检查以下配置:")
            print(f"- QINIU_ACCESS_KEY: {'✅' if settings.QINIU_ACCESS_KEY else '❌'}")
            print(f"- QINIU_SECRET_KEY: {'✅' if settings.QINIU_SECRET_KEY else '❌'}")
            print(f"- QINIU_BUCKET_NAME: {'✅' if settings.QINIU_BUCKET_NAME else '❌'}")
            print(f"- QINIU_DOMAIN: {'✅' if settings.QINIU_DOMAIN else '❌'}")
            return False
    else:
        print("✅ 使用本地存储")
        # 确保本地上传目录存在
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        print(f"本地上传目录: {upload_dir.absolute()}")
    
    return True

def run_migration():
    """运行数据库迁移"""
    print("🔄 运行数据库迁移...")
    
    try:
        from migration_add_storage_fields import migrate_database
        if migrate_database():
            print("✅ 数据库迁移完成")
            return True
        else:
            print("❌ 数据库迁移失败")
            return False
    except Exception as e:
        print(f"❌ 数据库迁移错误: {e}")
        return False

def start_server():
    """启动服务器"""
    print("🚀 启动服务器...")
    
    try:
        import uvicorn
        from main import app
        
        print(f"服务器启动在: http://{settings.HOST}:{settings.PORT}")
        print("API文档: http://localhost:8000/docs")
        print("按 Ctrl+C 停止服务器")
        
        uvicorn.run(
            app,
            host=settings.HOST,
            port=settings.PORT,
            reload=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 车辆图片管理系统启动器")
    print("=" * 50)
    
    # 检查步骤
    checks = [
        ("检查依赖包", check_dependencies),
        ("检查环境配置", check_env_file),
        ("检查数据库连接", check_database),
        ("检查存储配置", check_storage_config),
        ("运行数据库迁移", run_migration),
    ]
    
    for name, check_func in checks:
        if not check_func():
            print(f"\n❌ {name} 失败，请解决问题后重试")
            sys.exit(1)
    
    print("\n✅ 所有检查通过，准备启动服务器...")
    print(f"存储类型: {settings.STORAGE_TYPE}")
    print(f"数据库: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main() 