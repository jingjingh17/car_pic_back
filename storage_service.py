import base64
import mimetypes
from typing import Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
import io

class StorageService:
    def __init__(self):
        # BASE64存储不需要特殊配置
        pass
    
    async def upload_file(self, upload_file: UploadFile) -> dict:
        """
        上传文件并转换为BASE64（带压缩优化）
        返回格式: {
            "base64_data": "BASE64编码的图片数据",
            "thumbnail_data": "缩略图BASE64数据",
            "mime_type": "图片MIME类型",
            "size": "文件大小"
        }
        """
        if not upload_file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 检查文件类型
        content_type = upload_file.content_type
        if not content_type or not content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只允许上传图片文件")
        
        # 读取文件内容
        content = await upload_file.read()
        file_size = len(content)
        
        # 检查文件大小 (限制为5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if file_size > max_size:
            raise HTTPException(status_code=400, detail="文件大小不能超过5MB")
        
        # 压缩图片并转换为BASE64
        compressed_content = await self.compress_image(content, content_type)
        base64_data = base64.b64encode(compressed_content).decode('utf-8')
        
        # 构建完整的data URL格式（压缩后统一使用JPEG格式）
        data_url = f"data:image/jpeg;base64,{base64_data}"
        
        # 生成缩略图
        thumbnail_data = await self.create_thumbnail(compressed_content, "image/jpeg")
        
        return {
            "base64_data": data_url,
            "thumbnail_data": thumbnail_data,
            "mime_type": "image/jpeg",
            "size": len(compressed_content)
        }
    
    async def create_thumbnail(self, image_content: bytes, mime_type: str, max_width: int = 300, max_height: int = 200, quality: int = 85) -> str:
        """
        创建缩略图
        """
        try:
            # 使用PIL打开图片
            image = Image.open(io.BytesIO(image_content))
            
            # 转换为RGB模式（如果是RGBA，去除透明通道）
            if image.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 计算缩放比例
            width, height = image.size
            width_ratio = max_width / width
            height_ratio = max_height / height
            ratio = min(width_ratio, height_ratio)
            
            # 如果图片已经很小，不需要缩放
            if ratio >= 1:
                new_width, new_height = width, height
            else:
                new_width = int(width * ratio)
                new_height = int(height * ratio)
            
            # 调整图片大小
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 保存为JPEG格式的缩略图
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            thumbnail_content = output.getvalue()
            
            # 转换为BASE64
            thumbnail_base64 = base64.b64encode(thumbnail_content).decode('utf-8')
            thumbnail_data_url = f"data:image/jpeg;base64,{thumbnail_base64}"
            
            return thumbnail_data_url
            
        except Exception as e:
            # 如果缩略图生成失败，返回None
            print(f"生成缩略图失败: {e}")
            return None
    
    async def compress_image(self, image_content: bytes, mime_type: str, quality: int = 50, max_width: int = 1920, max_height: int = 1080) -> bytes:
        """
        压缩图片，降低质量以减小文件大小
        """
        try:
            # 使用PIL打开图片
            image = Image.open(io.BytesIO(image_content))
            
            # 转换为RGB模式（如果是RGBA，去除透明通道）
            if image.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 计算缩放比例（如果图片太大）
            width, height = image.size
            width_ratio = max_width / width
            height_ratio = max_height / height
            ratio = min(width_ratio, height_ratio)
            
            # 如果图片尺寸超过限制，进行缩放
            if ratio < 1:
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 保存为JPEG格式，使用指定的质量参数
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            compressed_content = output.getvalue()
            
            return compressed_content
            
        except Exception as e:
            # 如果压缩失败，返回原始内容
            print(f"图片压缩失败: {e}")
            return image_content
    
    async def delete_file(self, file_key: str) -> bool:
        """
        删除文件（BASE64存储中此操作无意义，总是返回True）
        """
        return True
    
    def get_file_url(self, base64_data: str) -> str:
        """
        获取文件访问URL（BASE64存储中直接返回data URL）
        """
        return base64_data
    
    def validate_base64_image(self, base64_data: str) -> bool:
        """
        验证BASE64图片数据是否有效
        """
        try:
            if not base64_data.startswith('data:image/'):
                return False
            
            # 提取BASE64部分
            if ';base64,' not in base64_data:
                return False
            
            base64_part = base64_data.split(';base64,')[1]
            
            # 尝试解码
            decoded = base64.b64decode(base64_part)
            
            # 检查是否为有效的图片格式（简单检查文件头）
            if decoded.startswith(b'\xff\xd8\xff'):  # JPEG
                return True
            elif decoded.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
                return True
            elif decoded.startswith(b'GIF87a') or decoded.startswith(b'GIF89a'):  # GIF
                return True
            elif decoded.startswith(b'RIFF') and b'WEBP' in decoded[:12]:  # WebP
                return True
            
            return False
            
        except Exception:
            return False
    
    def get_image_info(self, base64_data: str) -> dict:
        """
        获取BASE64图片的信息
        """
        if not self.validate_base64_image(base64_data):
            raise HTTPException(status_code=400, detail="无效的BASE64图片数据")
        
        try:
            # 提取MIME类型
            mime_type = base64_data.split(';')[0].replace('data:', '')
            
            # 提取BASE64部分并计算大小
            base64_part = base64_data.split(';base64,')[1]
            decoded = base64.b64decode(base64_part)
            size = len(decoded)
            
            return {
                "mime_type": mime_type,
                "size": size,
                "is_valid": True
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"解析BASE64图片数据失败: {str(e)}")

# 创建全局存储服务实例
storage_service = StorageService() 