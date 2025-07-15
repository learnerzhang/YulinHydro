# es_utils.py
import json
from elasticsearch import Elasticsearch, helpers
from config import ES_HOST, ES_PORT, ES_USERNAME, ES_PASSWORD

# ES连接配置
es = Elasticsearch([{'scheme': 'http', 'host': ES_HOST, 'port': ES_PORT}], basic_auth=(ES_USERNAME, ES_PASSWORD))

INDEX_NAME = "pdf_fragments"

# 创建索引（确保正确定义nested类型）
def create_index(force_recreate=False):
    index_exists = es.indices.exists(index=INDEX_NAME)
    # 强制删除重建索引
    if force_recreate and index_exists:
        es.indices.delete(index=INDEX_NAME)
        index_exists = False
        print(f"已删除并准备重建索引 {INDEX_NAME}")
    
    if not index_exists:
        mapping = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "ik_smart_analyzer": {
                            "type": "custom",
                            "tokenizer": "ik_smart"
                        },
                        "ik_max_analyzer": {
                            "type": "custom",
                            "tokenizer": "ik_max_word"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "document_id": {"type": "keyword"},
                    "document": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "text",
                                "analyzer": "ik_max_analyzer",  # 索引时细粒度分词
                                "search_analyzer": "ik_smart_analyzer"  # 搜索时粗粒度分词
                            },
                            "content": {
                                "type": "text",
                                "analyzer": "ik_max_analyzer",
                                "search_analyzer": "ik_smart_analyzer"
                            },
                            "metadata": {"type": "object"}
                        }
                    },
                    "fragments": {
                        "type": "nested",
                        "properties": {
                            "page_idx": {"type": "integer"},
                            "content": {
                                "type": "text",
                                "analyzer": "ik_max_analyzer",
                                "search_analyzer": "ik_smart_analyzer"
                            },
                            "bbox": {"type": "float"}
                        }
                    }
                }
            }
        }
        es.indices.create(index=INDEX_NAME, body=mapping)
        print(f"索引 {INDEX_NAME} 创建成功")
    elif not force_recreate:
        print(f"索引 {INDEX_NAME} 已存在")


def enhanced_search(query, search_in, page_size=10, page_number=1):
    # 检查索引是否存在且映射正确
    if not es.indices.exists(index=INDEX_NAME):
        create_index()
        return {"hits": {"hits": [], "total": {"value": 0}}}
    else:
        # 验证fragments字段是否为nested类型
        mapping = es.indices.get_mapping(index=INDEX_NAME)
        fragments_type = mapping[INDEX_NAME]['mappings']['properties'].get('fragments', {}).get('type')
        
        if fragments_type != 'nested':
            print(f"警告: fragments字段类型错误({fragments_type})，重建索引...")
            create_index(force_recreate=True)

    # 构建基础查询
    es_query = {
        "query": {
            "bool": {
                "should": []
            }
        },
        "from": (page_number - 1) * page_size,
        "size": page_size,
        "highlight": {
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"],
            "fields": {}
        }
    }

    # 添加搜索字段
    for field in search_in:
        if field == "fragments.content":
            # 嵌套字段的特殊处理
            nested_query = {
                "nested": {
                    "path": "fragments",
                    "query": {
                        "match": {
                            "fragments.content": {
                                "query": query,
                                "operator": "and",
                                "analyzer": "ik_smart_analyzer"  # 指定搜索时分词器
                            }
                        }
                    },
                    "inner_hits": {
                        "highlight": {
                            "fields": {"fragments.content": {}}
                        },
                        "size": 5
                    }
                }
            }
            es_query["query"]["bool"]["should"].append(nested_query)
        else:
            # 普通字段
            es_query["query"]["bool"]["should"].append({
                "match": {
                    field: {
                        "query": query,
                        "operator": "and",
                        "analyzer": "ik_smart_analyzer"  # 指定搜索时分词器
                    }
                }
            })
            # 添加高亮字段
            es_query["highlight"]["fields"][field] = {}

    # 输出查询
    print(json.dumps(es_query, indent=2))
    # 执行搜索
    try:
        results = es.search(index=INDEX_NAME, body=es_query)
        return results
    except Exception as e:
        print(f"ES搜索错误: {str(e)}")
        return {"hits": {"hits": [], "total": {"value": 0}}}

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
