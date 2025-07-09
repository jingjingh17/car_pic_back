import base64
import mimetypes
from typing import Optional
from fastapi import UploadFile, HTTPException

class StorageService:
    def __init__(self):
        # BASE64存储不需要特殊配置
        pass
    
    async def upload_file(self, upload_file: UploadFile) -> dict:
        """
        上传文件并转换为BASE64
        返回格式: {
            "base64_data": "BASE64编码的图片数据",
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
        
        # 转换为BASE64
        base64_data = base64.b64encode(content).decode('utf-8')
        
        # 构建完整的data URL格式
        data_url = f"data:{content_type};base64,{base64_data}"
        
        return {
            "base64_data": data_url,
            "mime_type": content_type,
            "size": file_size
        }
    
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