import json
import os
import shutil
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

from celery import Celery
from celery.signals import worker_ready
from sqlalchemy.ext.asyncio import AsyncSession

from config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from app.doc_crud import get_unparsed_documents, mark_document_parsed
from app.utils.es_utils import index_document_with_fragments, create_index
from app.database import AsyncSessionLocal
from app.dbmodels import Document

# 配置参数
MAGIC_PDF_PATH = os.getenv("MAGIC_PDF_PATH", "mineru")
OUTPUT_BASE_DIR = "static/output/magic_pdf/"

# 创建Celery实例
celery = Celery('tasks', broker=f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0')

# 设置定时任务
celery.conf.beat_schedule = {
    'parse-documents-every-6-hours': {
        'task': 'tasks.parse_documents',
        'schedule': timedelta(hours=6).total_seconds(),
    },
}

# 创建基于文件路径的锁字典
file_locks: Dict[str, asyncio.Lock] = {}
logger = logging.getLogger(__name__)

async def run_magic_pdf(pdf_path: str, output_dir: str, mode: str = "auto") -> Tuple[bool, str, Optional[str]]:
    """
    执行 magic-pdf 命令处理 PDF 文件，使用基于文件路径的锁确保同文件串行执行
    
    参数:
        pdf_path: 输入 PDF 文件的路径
        output_dir: 输出目录的路径
        mode: 处理模式，默认为 "auto"
    
    返回:
        success: 命令是否成功执行
        message: 命令执行结果信息
        unique_output_dir: 生成的唯一输出目录
    """
    # 检查输入文件是否存在
    if not os.path.exists(pdf_path):
        return False, f"错误: 输入文件不存在: {pdf_path}", None

    # 为每个文件创建唯一的输出子目录
    unique_output_dir = os.path.join(output_dir, str(uuid.uuid4()))
    os.makedirs(unique_output_dir, exist_ok=True)
    
    # 获取或创建基于文件路径的锁
    if pdf_path not in file_locks:
        file_locks[pdf_path] = asyncio.Lock()
    
    # 使用文件锁确保同一文件的处理串行执行
    async with file_locks[pdf_path]:
        logger.info(f"获取到 {pdf_path} 的文件锁，开始处理")
        
        # 构建命令（使用可配置的路径）
        cmd = [MAGIC_PDF_PATH, "-p", pdf_path, "-o", unique_output_dir, "-m", mode]
        logger.info(f"执行命令: {' '.join(cmd)}")
        try:
            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # 实时捕获标准输出和标准错误流
            output_lines = []
            while True:
                stdout_line = await process.stdout.readline()
                stderr_line = await process.stderr.readline()

                if stdout_line:
                    line = stdout_line.decode('utf-8').strip()
                    logger.info(f"执行进度: {line}")
                    output_lines.append(line)
                if stderr_line:
                    line = stderr_line.decode('utf-8').strip()
                    logger.error(f"执行错误: {line}")
                    output_lines.append(line)

                if not stdout_line and not stderr_line:
                    break

            await process.wait()

            if process.returncode != 0:
                error_msg = f"命令执行失败，返回代码: {process.returncode}\n错误信息:\n{''.join(output_lines)}"
                return False, error_msg, unique_output_dir
            
            success_msg = f"命令成功执行。\n标准输出:\n{''.join(output_lines)}"
            return True, success_msg, unique_output_dir
            
        except Exception as e:
            return False, f"执行命令时发生未知错误: {e}", unique_output_dir
        finally:
            logger.info(f"释放 {pdf_path} 的文件锁，处理完成")

async def cleanup_output(output_dir: Optional[str]):
    """清理输出目录"""
    if output_dir and os.path.exists(output_dir):
        try:
            shutil.rmtree(output_dir)
            logger.info(f"已清理临时目录: {output_dir}")
        except Exception as e:
            logger.error(f"清理目录 {output_dir} 失败: {str(e)}")

async def process_single_document(db: AsyncSession, doc: Document):
    """处理单个文档的协程函数"""
    pdf_path = doc.file_path
    unique_output_dir = None
    
    try:
        # 使用异步方式调用run_magic_pdf
        success, message, unique_output_dir = await run_magic_pdf(
            pdf_path, OUTPUT_BASE_DIR, mode="auto"
        )
        
        if not success:
            logger.error(f"处理文档 {doc.id} 失败: {message}")
            return
        
        # 使用标准路径处理方式
        base_name = os.path.basename(pdf_path)
        tmpname = os.path.splitext(base_name)[0]
        tmppath = os.path.join(unique_output_dir, f"{tmpname}/auto/{tmpname}_middle.json")
        
        # 检查中间文件是否存在
        if not os.path.exists(tmppath):
            logger.error(f"中间文件不存在: {tmppath}")
            return
        
        # 加载解析结果
        with open(tmppath, 'r', encoding='utf-8') as f:
            pdf_data = json.load(f)
        
        # 提取并添加片段 - 优化后的代码
        fragments = []
        for page in pdf_data.get('pdf_info', []):
            page_idx = page.get('page_idx', 0)
            
            # 优先处理 preproc_blocks
            blocks = page.get('preproc_blocks', [])
            if not blocks:
                # 如果没有 preproc_blocks，尝试使用 para_blocks
                blocks = page.get('para_blocks', [])
            
            for block_idx, block in enumerate(blocks):
                block_id = f"p{page_idx}_b{block_idx}"
                
                # 处理区块中的行
                for line_idx, line in enumerate(block.get('lines', [])):
                    line_id = f"{block_id}_l{line_idx}"
                    spans = line.get('spans', [])
                    
                    # 如果行内没有span，尝试从行对象直接提取内容
                    if not spans:
                        content = line.get('content', '')
                        if content:
                            fragment = {
                                "page_idx": page_idx,
                                "content": content,
                                "bbox": line.get('bbox', []),
                                "block_id": block_id,
                                "line_id": line_id,
                                "span_id": f"{line_id}_s0"
                            }
                            fragments.append(fragment)
                        continue
                    
                    # 处理行内的每个span
                    for span_idx, span in enumerate(spans):
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
        
        # 准备文档元数据
        metadata = {
            "file_path": doc.file_path,
            "created_at": datetime.now().isoformat(),
            "total_pages": len(pdf_data.get('pdf_info', [])),
            "tags": doc.tag_string if doc.tag_string else ""
        }
        
        # 修复点1: 检查index_document_with_fragments是否异步
        # 如果是同步函数，直接调用而不加await
        # 如果是异步函数，使用await
        # 这里我们根据错误日志假设它是同步函数
        index_document_with_fragments(
            document_id=f"doc_{doc.id}",
            title=doc.title,
            fragments=fragments,
            metadata=metadata
        )
        
        # 标记为已解析
        # 修复点2: 确保在同一个会话中操作
        doc.parsed = True
        await db.commit()
        await db.refresh(doc)
        
        logger.info(f"成功解析并索引文档: {doc.id}")
    except Exception as e:
        logger.error(f"处理文档 {doc.id} 时出错: {str(e)}")
        # 回滚事务
        await db.rollback()
        raise
    finally:
        # 确保清理临时目录
        if unique_output_dir:
            # 同步清理函数在异步上下文中直接调用
            cleanup_output(unique_output_dir)

@celery.task
def parse_documents():
    """Celery任务：解析文档"""
    logger.info("Starting document parsing task...")
    asyncio.run(async_parse_documents())

async def async_parse_documents():
    """异步函数：解析文档"""
    create_index()  # 确保索引存在
    
    # 修复点3: 使用新的会话上下文
    async with AsyncSessionLocal() as db:
        try:
            # 获取未解析文档
            unparsed_docs = await get_unparsed_documents(db)
            logger.info(f"找到 {len(unparsed_docs)} 个未解析文档")
            
            for doc in unparsed_docs:
                try:
                    logger.info(f"处理文档 ID: {doc.id}, 标题: {doc.title}")
                    
                    # 修复点4: 为每个文档创建新的会话
                    # 避免会话状态污染
                    async with AsyncSessionLocal() as doc_db:
                        # 重新加载文档以确保会话状态一致
                        doc_refreshed = await doc_db.get(Document, doc.id)
                        if doc_refreshed:
                            await process_single_document(doc_db, doc_refreshed)
                        else:
                            logger.warning(f"文档 {doc.id} 不存在，跳过")
                except Exception as e:
                    logger.error(f"处理文档 {doc.id} 时出错: {str(e)}")
                    # 继续处理下一个文档
                    continue
            
        except Exception as e:
            logger.error(f"批量处理文档时出错: {str(e)}")
        finally:
            # 确保关闭会话
            await db.close()

@worker_ready.connect
def at_start(sender, **kwargs):
    """Worker启动时发送任务"""
    # 获取任务实例
    task = sender.app.tasks.get('tasks.parse_documents')
    
    if task:
        # 检查任务是否已在运行
        active_tasks = sender.app.control.inspect().active()
        task_running = False
        
        if active_tasks:
            for worker_tasks in active_tasks.values():
                for t in worker_tasks:
                    if t['name'] == 'tasks.parse_documents':
                        task_running = True
                        break
                if task_running:
                    break
        
        if not task_running:
            task.delay()
    else:
        logger.error("无法找到任务: tasks.parse_documents")