import hashlib
import os
import asyncio
from pathlib import Path
from app.database import AsyncSessionLocal, create_table
from app.dbmodels import Base, Document
from app.doc_crud import create_document, get_document_by_file_path  # 需新增查询方法
from config import UPLOAD_FOLDER

async def import_pdfs_from_directory(directory: str):
    """从指定目录导入所有PDF文件到数据库"""
    # 确保上传目录存在
    Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
    
    # 初始化数据库表
    await create_table(Base)
    
    async with AsyncSessionLocal() as db:
        # 遍历目录下的PDF文件
        for filename in os.listdir(directory):
            if filename.lower().endswith(".pdf"):
                source_path = os.path.join(directory, filename)
                # 构造目标路径（避免重名）
                with open(source_path, "rb") as f:
                    file_content = f.read()
                    file_hash = hashlib.sha256(file_content).hexdigest()
                
                # 构建新的文件名和路径
                new_filename = f"{file_hash}.pdf"
                target_path = os.path.join(UPLOAD_FOLDER, new_filename)
                    
                counter = 1
                while os.path.exists(target_path):
                    name, ext = os.path.splitext(new_filename)
                    target_path = os.path.join(UPLOAD_FOLDER, f"{name}_{counter}{ext}")
                    counter += 1
                
                # 检查是否已导入
                existing_doc = await get_document_by_file_path(db, target_path)
                if existing_doc:
                    print(f"已存在: {filename}")
                    continue
                
                # 复制文件到上传目录
                with open(source_path, "rb") as fsrc, open(target_path, "wb") as fdst:
                    fdst.write(fsrc.read())
                
                # 创建数据库记录
                doc = await create_document(
                    db=db,
                    title=os.path.splitext(filename)[0],
                    description=f"导入自: {source_path}",
                    content="",  # 内容由后续解析任务填充
                    tags="",
                    file_path=target_path,
                    file_type="pdf"
                )
                print(f"导入成功: {filename} (ID: {doc.id})")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print(f"用法: {sys.argv[0]} <PDF目录路径>")
        sys.exit(1)
    
    pdf_directory = sys.argv[1]
    if not os.path.isdir(pdf_directory):
        print(f"错误: {pdf_directory} 不是有效目录")
        sys.exit(1)
    
    asyncio.run(import_pdfs_from_directory(pdf_directory))