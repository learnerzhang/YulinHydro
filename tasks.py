# celery_tasks.py
from asyncio.log import logger
import json
import os
import pdfplumber
from celery import Celery
from config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from app.doc_crud import get_unparsed_documents, mark_document_parsed
from app.database import AsyncSessionLocal
from app.utils.es_utils import index_document_with_fragments, create_index
import subprocess
from datetime import datetime
import asyncio  # 新增导入
import os

# 创建Celery实例
celery = Celery('tasks', broker=f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0')
# 设置定时任务
celery.conf.beat_schedule = {
    'parse-documents-every-10-minutes': {
        'task': 'tasks.parse_documents',
        'schedule': 60,  # 每X分钟
    },
}

def run_magic_pdf(pdf_path, output_dir, mode="auto"):
    """
    执行 magic-pdf 命令处理 PDF 文件

    参数:
        pdf_path (str): 输入 PDF 文件的路径
        output_dir (str): 输出目录的路径
        mode (str): 处理模式，默认为 "auto"

    返回:
        bool: 命令是否成功执行
        str: 命令执行结果信息
    """
    # 检查输入文件是否存在
    if not os.path.exists(pdf_path):
        return False, f"错误: 输入文件不存在: {pdf_path}"

    # 检查输出目录是否存在，不存在则创建
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            return False, f"错误: 无法创建输出目录: {output_dir}，错误: {e}"

    # 构建命令
    cmd = ["magic-pdf", "-p", pdf_path, "-o", output_dir, "-m", mode]

    try:
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, f"命令成功执行。\n标准输出:\n{result.stdout}"

    except subprocess.CalledProcessError as e:
        return False, f"命令执行失败，返回代码: {e.returncode}\n错误信息:\n{e.stderr}"

    except Exception as e:
        return False, f"执行命令时发生未知错误: {e}"

 

# 新增异步处理函数
async def async_parse_documents():
    logger.info("Starting document parsing task...")
    create_index()  # 确保索引存在
    
    async with AsyncSessionLocal() as session:
        # 获取未解析文档
        unparsed_docs = await get_unparsed_documents(session)  # 添加 await
        
        for doc in unparsed_docs:
            # print(doc.file_path)
            # print("URL:", f'http://app-server:5000/{doc.file_path}')
            # from gradio_client import Client, handle_file
            # client = Client("http://app-server:8001/")
            # result = client.predict(
            #         file_path=handle_file(f'http://app-server:5000/{doc.file_path}'),
            #         api_name="/to_pdf"
            # )
            # print(result)
            # magic-pdf -p {some_pdf} -o {some_output_dir} -m auto
            pdf_path = doc.file_path
            output_dir = f"static/output/magic_pdf/{doc.id}"
            success, message = run_magic_pdf(pdf_path, output_dir, mode="auto")
            if success:
                logger.info(f"Successfully processed document: {doc.id}")
            else:
                logger.error(f"Error processing document {doc.id}: {message}")
                continue
            try:
                # 加载并索引文档和片段
                tmppath = f"{output_dir}/auto/{doc.title}_middle.json"
                if not os.path.exists(tmppath):
                    continue
               
                with open(tmppath, 'r', encoding='utf-8') as f:
                    pdf_data = json.load(f)


                # 提取并添加片段
                fragments = []
                for page in pdf_data:
                    page_idx = page.get('page_idx', 0)
                    for block_idx, block in enumerate(page.get('preproc_blocks', [])):
                        block_id = f"p{page_idx}_b{block_idx}"
                        for line_idx, line in enumerate(block.get('lines', [])):
                            line_id = f"{block_id}_l{line_idx}"
                            for span_idx, span in enumerate(line.get('spans', [])):
                                span_id = f"{line_id}_s{span_idx}"
                                content = span.get('content', '')
                                if content:
                                    fragment = {
                                        "page_idx": page_idx,
                                        "content": content,
                                        "bbox": span.get('bbox', []),
                                        "block_id": block_id,
                                        "line_id": line_id,
                                        "span_id": span_id
                                    }
                                    fragments.append(fragment)

                # 索引文档
                metadata = {
                    "file_path": doc.file_path,
                    "created_at": datetime.now().isoformat(),
                    "tags": doc.tags
                }
                
                index_document_with_fragments(
                    document_id=doc.id,
                    title=doc.title,
                    fragments=fragments,
                    metadata=metadata
                )
                
                # 标记为已解析
                await mark_document_parsed(session, doc.id)  # 添加 await
                await session.commit()  # 添加 await
                
                logger.info(f"Successfully parsed and indexed document: {doc.id}")
                pass
            except Exception as e:
                logger.error(f"Error processing document {doc.id}: {str(e)}")
                # 发生错误时回滚
                await session.rollback()  # 添加 await

@celery.task
def parse_documents():
    # 在同步上下文中运行异步函数
    asyncio.run(async_parse_documents())