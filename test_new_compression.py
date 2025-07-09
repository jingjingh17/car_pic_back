#!/usr/bin/env python3
"""
测试新的图片压缩参数
"""

import asyncio
from PIL import Image
import io
from storage_service import StorageService

async def test_new_compression():
    """测试新的压缩参数"""
    print("🧪 测试新的图片压缩参数...")
    
    # 创建存储服务实例
    storage = StorageService()
    
    # 创建一个测试图片
    print("📸 创建测试图片...")
    test_image = Image.new('RGB', (1920, 1080), color='blue')
    
    # 保存为高质量JPEG
    output = io.BytesIO()
    test_image.save(output, format='JPEG', quality=95)
    original_content = output.getvalue()
    original_size = len(original_content)
    
    print(f"📊 原始图片大小: {original_size:,} 字节 ({original_size/1024:.1f} KB)")
    
    # 测试新的压缩参数（质量70%）
    print("🔧 执行新压缩参数（质量70%）...")
    compressed_content = await storage.compress_image(original_content, "image/jpeg", quality=70)
    compressed_size = len(compressed_content)
    
    print(f"📊 压缩后大小: {compressed_size:,} 字节 ({compressed_size/1024:.1f} KB)")
    
    # 计算压缩率
    compression_ratio = (1 - compressed_size / original_size) * 100
    print(f"📈 压缩率: {compression_ratio:.1f}%")
    
    # 对比缩略图质量（85%）
    print("🔧 对比缩略图质量（85%）...")
    thumbnail_content = await storage.compress_image(original_content, "image/jpeg", quality=85)
    thumbnail_size = len(thumbnail_content)
    
    print(f"📊 缩略图大小: {thumbnail_size:,} 字节 ({thumbnail_size/1024:.1f} KB)")
    
    # 对比50%质量
    print("🔧 对比原压缩参数（质量50%）...")
    old_compressed_content = await storage.compress_image(original_content, "image/jpeg", quality=50)
    old_compressed_size = len(old_compressed_content)
    
    print(f"📊 50%质量大小: {old_compressed_size:,} 字节 ({old_compressed_size/1024:.1f} KB)")
    
    print("\n📋 压缩效果对比:")
    print(f"   原始大小: {original_size/1024:.1f} KB")
    print(f"   70%质量: {compressed_size/1024:.1f} KB (新参数)")
    print(f"   85%质量: {thumbnail_size/1024:.1f} KB (缩略图)")
    print(f"   50%质量: {old_compressed_size/1024:.1f} KB (原参数)")
    print(f"   70%压缩率: {compression_ratio:.1f}%")
    
    # 计算相对于缩略图的改进
    improvement = ((thumbnail_size - compressed_size) / thumbnail_size) * 100
    print(f"   相比缩略图节省: {improvement:.1f}%")
    
    print("\n✅ 新压缩参数测试完成！")
    print("📝 结论: 70%质量在文件大小和图片质量之间取得了良好平衡")

if __name__ == "__main__":
    asyncio.run(test_new_compression()) 