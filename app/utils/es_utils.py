# es_utils.py
import json
from elasticsearch import Elasticsearch, helpers
from config import ES_HOST, ES_PORT, ES_USERNAME, ES_PASSWORD

# ES连接配置
es = Elasticsearch([{'scheme': 'http', 'host': ES_HOST, 'port': ES_PORT}], 
                  basic_auth=(ES_USERNAME, ES_PASSWORD))

INDEX_NAME = "pdf_fragments"

# 创建索引
def create_index():
    if not es.indices.exists(index=INDEX_NAME):
        mapping = {
            "mappings": {
                "properties": {
                    "document_id": {"type": "keyword"},
                    "document": {
                        "properties": {
                            "title": {"type": "text"},
                            "author": {"type": "text"},
                            "content": {"type": "text"},
                            "metadata": {"type": "object"}
                        }
                    },
                    "fragments": {
                        "type": "nested",
                        "properties": {
                            "page_idx": {"type": "integer"},
                            "content": {"type": "text"},
                            "bbox": {"type": "float"},
                            "block_id": {"type": "keyword"},
                            "line_id": {"type": "keyword"},
                            "span_id": {"type": "keyword"}
                        }
                    }
                }
            }
        }
        es.indices.create(index=INDEX_NAME, body=mapping)

# 索引文档（带片段）
def index_document_with_fragments(document_id, title, fragments, metadata=None):
    if metadata is None:
        metadata = {}
    
    # 构建文档全文内容
    document_content = " ".join(frag['content'] for frag in fragments)
    
    doc = {
        "document_id": document_id,
        "document": {
            "title": title,
            "author": "系统生成",
            "content": document_content,
            "metadata": metadata
        },
        "fragments": fragments
    }
    
    es.index(index=INDEX_NAME, id=document_id, body=doc)
    return True

# 删除文档
def delete_document_from_es(doc_id):
    """删除文档索引"""
    es.delete(index=INDEX_NAME, id=doc_id, ignore=[404])
    return True

# 增强搜索
def enhanced_search(query, search_in, page_size=10, page_number=1):
    # 构建多字段查询
    multi_match_query = {
        "multi_match": {
            "query": query,
            "fields": search_in,
            "operator": "and",
            "fuzziness": "AUTO"
        }
    }
    
    # 构建完整查询
    es_query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "nested": {
                            "path": "fragments",
                            "query": {
                                "match": {
                                    "fragments.content": {
                                        "query": query,
                                        "operator": "and",
                                        "fuzziness": "AUTO"
                                    }
                                }
                            },
                            "inner_hits": {
                                "highlight": {
                                    "fields": {"fragments.content": {}},
                                    "pre_tags": ["<mark>"],
                                    "post_tags": ["</mark>"]
                                },
                                "size": 5
                            }
                        }
                    },
                    {
                        "match": {
                            "document.content": {
                                "query": query,
                                "operator": "and",
                                "fuzziness": "AUTO"
                            }
                        }
                    }
                ]
            }
        },
        "highlight": {
            "fields": {"document.content": {}},
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"]
        },
        "from": (page_number - 1) * page_size,
        "size": page_size
    }
    
    # 执行搜索
    results = es.search(index=INDEX_NAME, body=es_query)
    return results