import logging
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status, Cookie, Response
from sqlalchemy import func, select
from app import base_crud, dbmodels, schemas, utils
from app.dbmodels import User
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from app.database import AsyncSessionLocal, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Response, Cookie
from sqlalchemy.orm import Session
from docxtpl import DocxTemplate

import tempfile
import string
import json
import jwt
import io
import os
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

@router.get("/")
async def read_root():
    return {"Hello": "World"}

class PingGuBase(BaseModel):
    startdate: str="20240101"
    enddate: str="20241231"
    regions: List[str] = ["yuyang", "hengshan"]
    disasterType: str="FLOOD"
    selectAll: bool = False

# 文件服务器路由 - 用于下载生成的文件
@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = Path("static/output/zqpg") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(file_path, filename=filename)


@router.post("/makeword")
async def makezqpgword(pinggu: PingGuBase):
    """
    根据template.json参数填充Word模板并生成新文件
    返回新生成Word文件的HTTP下载URL
    """
    print("request:", pinggu)
    json_path = "static/template.json"

    try:
        # 解析JSON参数
        with open(json_path, 'r', encoding='utf-8') as f:
            params = json.load(f)['data']
        if pinggu.disasterType == "FLOOD":
            from app import kg_flood
            template_path = "static/FLOOD_TEMPLETE.docx"
            doc = DocxTemplate(template_path)
            params['startdate'] = params['startDate']
            params['enddate'] = params['endDate']
            params['publicdate'] = datetime.now().strftime('%Y年%m月%d日')
            params['zqzs'] = kg_flood.get_zhgk(params)
            params['slgcssssqk'] = kg_flood.get_slgcssssqk(params)
            params['zdslgcsgqk'] = kg_flood.get_zdslgcsgqk(params)
            params['czsyqk'] = kg_flood.get_czsyqk(params)
            params['khqxjszcqk'] = kg_flood.get_khqxjszcqk(params)
            params['shzhfyqk'] = kg_flood.get_shzhfyqk(params)
            params['zdszdqfx'] = kg_flood.get_zdszdqfx(params)
        elif pinggu.disasterType == "DROUGHT":
            from app import kg_drought
            # 灾情类型，枚举值：FLOOD（洪涝灾害）、DROUGHT（干旱灾害）
            template_path = "static/DROUGHT_TEMPLETE.docx"
            doc = DocxTemplate(template_path)
            params['startdate'] = params['startDate']
            params['enddate'] = params['endDate']
            params['publicdate'] = datetime.now().strftime('%Y年%m月%d日')
            params['zqzs'] = kg_drought.get_zqzs(params)
            params['dqnyhqzk'] = kg_drought.get_dqnyhqzk(params)
            params['slgcxssyzk'] = kg_drought.get_slgcxssyzk(params)
            params['khtrzzqk'] = kg_drought.get_khtrzzqk(params)
            params['khcxjzxy'] = kg_drought.get_khcxjzxy(params)
            params['zdshdqqk'] = kg_drought.get_zdshdqqk(params)
        # 渲染模板
        doc.render(params)
        # 确保输出目录存在
        output_dirpath = "static/output/zqpg"
        output_dir = Path(output_dirpath)
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"灾情评估报告_{params['startdate']}_{params['enddate']}.docx"
        file_path = output_dir / filename
        
        # 保存新文件
        doc.save(str(file_path))
        download_url = f"{output_dirpath}/{filename}"
        return {"message": "文件生成成功", "download_url": download_url}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文件生成失败：{str(e)}"
        )