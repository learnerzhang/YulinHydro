import json
import os
import pprint
import shutil
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from app.utils.es_utils import index_document_with_fragments, create_index

logger = logging.getLogger(__name__)

def process_single_document():
    """处理单个文档的协程函数"""
    unique_output_dir = "static/output/magic_pdf/eddb5dee-fa9f-43e0-aeb0-85c82f50df16"
    pdf_path = 'static/documents/2f50b0c93ece656eb39aeeb638c5d3522cc01362d439096239f389033753ae01.pdf'
    base_name = os.path.basename(pdf_path)
    tmpname = os.path.splitext(base_name)[0]
    tmppath = os.path.join(unique_output_dir, f"{tmpname}/auto/{tmpname}_middle.json")
    print(f"parsed path: {tmppath}")
    # 检查中间文件是否存在
    if not os.path.exists(tmppath):
        # logger.error(f"中间文件不存在: {tmppath}")
        print(f"中间文件不存在: {tmppath}")
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
        "file_path": pdf_path,
        "created_at": datetime.now().isoformat(),
        "tags": "群聊日报,AI技术",
        "total_pages": len(pdf_data.get('pdf_info', [])),
        "source": "kimi.ai生成"
    }
    # pprint.pprint(fragments)
    # 索引文档
    rt = index_document_with_fragments(
        document_id=f"doc_{uuid.uuid4().hex}",  # 生成唯一ID
        title="2025-07-04群聊日报",
        fragments=fragments,
        metadata=metadata
    )
    
    print(f"成功解析并索引文档，共提取{fragments}个片段", rt)

process_single_document()
