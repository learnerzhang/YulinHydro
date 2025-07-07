# es_utils.py
from elasticsearch import Elasticsearch, helpers
from config import ES_HOST, ES_PORT, ES_USERNAME, ES_PASSWORD

# ES连接配置
es = Elasticsearch(
    [{'scheme': 'http', 'host': ES_HOST, 'port': ES_PORT}],
    basic_auth=(ES_USERNAME, ES_PASSWORD)
)

INDEX_NAME = "documents"

def create_index():
    """创建ES索引"""
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body={
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                    "description": {"type": "text", "analyzer": "ik_max_word"},
                    "content": {"type": "text", "analyzer": "ik_max_word"},
                    "tags": {"type": "keyword"},
                    "file_path": {"type": "keyword"}
                }
            }
        })

def index_document(doc_id, title, description, content, tags, file_path):
    """添加/更新文档索引"""
    body = {
        'id': doc_id,
        'title': title,
        'description': description,
        'content': content,
        'tags': tags,
        'file_path': file_path
    }
    es.index(index=INDEX_NAME, id=doc_id, body=body)

def delete_document(doc_id):
    """删除文档索引"""
    es.delete(index=INDEX_NAME, id=doc_id, ignore=[404])

def search_documents(query, page=1, size=10):
    """搜索文档"""
    if not es.indices.exists(index=INDEX_NAME):
        create_index()
        
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^3", "description^2", "content", "tags"]
            }
        },
        "from": (page - 1) * size,
        "size": size
    }
    return es.search(index=INDEX_NAME, body=body)

# 其他ES操作函数