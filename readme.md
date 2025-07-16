## 服务 启动方式（需要ES服务，见docker）
##### python main.py

### 定时解析PDF
##### celery -A tasks beat --loglevel=info
##### celery -A tasks worker --loglevel=info


### 离线灌入数据
##### python import_pdfs.py

## 依赖
##### pip install -r requirements.txt

#### PDF OCR工具
 
#### https://github.com/opendatalab/MinerU

`
pip install --upgrade pip
pip install uv
uv pip install -U "mineru[core]"
`

## ES分词器
### bin/elasticsearch-plugin install https://get.infini.cloud/elasticsearch/analysis-ik/7.17.2

##### 版本要和本地的ES环境保持一致


## 修改字段，只需要删表, 启动服务
##### 启动应用后，接口访问 http://localhost:5000/docs

