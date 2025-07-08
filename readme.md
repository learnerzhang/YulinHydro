# 启动方式
### python main.py
### uvicorn main:app --reload --port 5000 --host 0.0.0.0


# 依赖
### pip install -r requirements.txt

# ES
### bin/elasticsearch-plugin install https://get.infini.cloud/elasticsearch/analysis-ik/8.4.1
### 版本要和本地的ES环境保持一致


# 重建表, 删除表，启动服务
### 启动应用后，访问 http://localhost:5000/docs