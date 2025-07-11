from asyncio.log import logger
import json
import os
from celery import Celery
from config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from app.doc_crud import get_unparsed_documents, mark_document_parsed
from app.database import AsyncSessionLocal
from app.utils.es_utils import index_document_with_fragments, create_index
import subprocess
from celery.signals import worker_ready
from datetime import datetime
import asyncio
import uuid

# 创建Celery实例
celery = Celery('tasks', broker=f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0')
# 设置定时任务
celery.conf.beat_schedule = {
    'parse-documents-every-6-hours': {
        'task': 'tasks.parse_documents',
      'schedule': 60 * 60 * 6,  # 每6小时
    },
}

# 创建全局异步锁
pdf_processing_lock = asyncio.Lock()

async def run_magic_pdf(pdf_path, output_dir, mode="auto"):
    """
    执行 magic-pdf 命令处理 PDF 文件，使用异步锁确保串行执行

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

    # 为每个文件创建唯一的输出子目录
    unique_output_dir = os.path.join(output_dir, str(uuid.uuid4()))
    os.makedirs(unique_output_dir, exist_ok=True)

    # 使用异步锁确保同一时间只有一个协程可以执行magic-pdf命令
    async with pdf_processing_lock:
        logger.info(f"获取到锁，开始处理文件: {pdf_path}")
        # 构建命令
        cmd = ["mineru", "-p", pdf_path, "-o", unique_output_dir, "-m", mode]

        try:
            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                return False, f"命令执行失败，返回代码: {process.returncode}\n错误信息:\n{stderr.decode('utf-8')}"

            return True, f"命令成功执行。\n标准输出:\n{stdout.decode('utf-8')}", unique_output_dir

        except Exception as e:
            return False, f"执行命令时发生未知错误: {e}", None
        finally:
            logger.info(f"释放锁，文件处理完成: {pdf_path}")


# 新增异步处理函数
async def async_parse_documents():
    logger.info("Starting document parsing task...")
    create_index()  # 确保索引存在

    async with AsyncSessionLocal() as session:
        # 获取未解析文档
        unparsed_docs = await get_unparsed_documents(session)

        for doc in unparsed_docs:
            pdf_path = doc.file_path
            output_dir = f"static/output/magic_pdf/"
            # 使用异步方式调用run_magic_pdf
            success, message, unique_output_dir = await run_magic_pdf(pdf_path, output_dir, mode="auto")
            if not success:
                logger.error(f"Error processing document {doc.id}: {message}")
                continue

            try:
                # 加载并索引文档和片段
                tmpname = doc.path.split('/')[-1].split('.')[0]
                tmppath = os.path.join(unique_output_dir, f"{tmpname}/auto/{tmpname}_middle.json")
                if not os.path.exists(tmppath):
                    continue

                with open(tmppath, 'r', encoding='utf-8') as f:
                    pdf_data = json.load(f)

                # 提取并添加片段
                fragments = []
                for page in pdf_data.get('pages', []):
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
                await mark_document_parsed(session, doc.id)
                await session.commit()

                logger.info(f"Successfully parsed and indexed document: {doc.id}")
            except Exception as e:
                logger.error(f"Error processing document {doc.id}: {str(e)}")
                # 发生错误时回滚
                await session.rollback()


@celery.task
def parse_documents():
    # 在同步上下文中运行异步函数
    asyncio.run(async_parse_documents())


@worker_ready.connect
def at_start(sender, **kwargs):
    # 在 worker 启动时发送任务
    with sender.app.connection() as conn:
        sender.app.send_task('tasks.parse_documents', connection=conn)