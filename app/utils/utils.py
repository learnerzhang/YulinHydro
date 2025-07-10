import os
import numpy as np
import shutil
from datetime import datetime
from fastapi import UploadFile, HTTPException, status
from config import UPLOAD_FOLDER

# 初始化MTCNN和人脸识别模型

def get_file_path(filename: str):
    return os.path.join(UPLOAD_FOLDER, filename)

# 创建上传文件夹（如果不存在）
def create_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

# 保存上传的文件
def save_uploaded_file(file: UploadFile, directory: str = UPLOAD_FOLDER) -> str:
    create_upload_folder()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(directory, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"保存文件失败: {str(e)}")
    finally:
        file.file.close()
    
    return filename


    