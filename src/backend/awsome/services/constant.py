from pymilvus import FieldSchema, DataType

from awsome.settings import get_config

"""
Milvus 默认配置项
"""
milvus_default_fields_1024 = [
    FieldSchema(name="bbox", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="start_page", dtype=DataType.INT64),
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="chunk_index", dtype=DataType.INT64),
    FieldSchema(name="extra", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="file_id", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="knowledge_id", dtype=DataType.VARCHAR, max_length=65535, is_partition_key=True),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1024)
]

milvus_default_fields_768 = [
    FieldSchema(name="bbox", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="start_page", dtype=DataType.INT64),
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="chunk_index", dtype=DataType.INT64),
    FieldSchema(name="extra", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="file_id", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="knowledge_id", dtype=DataType.VARCHAR, max_length=65535, is_partition_key=True),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=768)
]

"""
Milvus 索引参数
"""
milvus_default_index_params = {
    "index_type": "HNSW",
    "metric_type": "L2",
    "params": {
        "M": 8,
        "efConstruction": 64
    }
}

"""
常量
"""
# 系统默认启用模型
redis_default_model_key = "awsome_default_system_model"

"""
记忆默认配置
"""
memory_config = {
    "llm": {  # LLM配置
        "provider": "openai",
        "config": {
            "model": get_config("memory_only.llm.llm_name"),
            "temperature": 0.1,
            "max_tokens": 2000,
            "top_p": 0.3,
            "api_key": get_config("memory_only.llm.api_key"),
            "openai_base_url": get_config("memory_only.llm.base_url")
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": get_config("memory_only.embedding.embedding_name"),
            "embedding_dims": get_config("memory_only.embedding.dimension"),
            "api_key": get_config("memory_only.embedding.api_key"),
            "openai_base_url": get_config("memory_only.embedding.base_url")
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            # "url": "neo4j+s://localhost:7687",
            "url": get_config("memory_only.neo4j.url"),
            "username": get_config("memory_only.neo4j.username"),
            "password": get_config("memory_only.neo4j.password"),
        }
    },
    "vector_store": {
        "provider": "milvus",
        "config": {
            "collection_name": get_config("memory_only.milvus_memory_name"),
            "embedding_model_dims": get_config("memory_only.embedding.dimension"),
            "url": get_config("storage.milvus.uri")
        }
    },
    "version": "v1.1"  # v1.1配置支持Graph
}