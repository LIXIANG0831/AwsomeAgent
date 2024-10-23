import os
from mem0 import Memory
from awsome.settings import get_config

os.environ["OPENAI_API_KEY"] = get_config("api.openai.api_key")
os.environ["OPENAI_BASE_URL"] = get_config("api.openai.base_url")

os.environ["LLM_AZURE_OPENAI_API_KEY"] = get_config('api.azure.openai.api_key')
os.environ["LLM_AZURE_DEPLOYMENT"] = get_config('api.azure.openai.azure_deployment')
os.environ["LLM_AZURE_ENDPOINT"] = get_config('api.azure.openai.azure_endpoint')
os.environ["LLM_AZURE_API_VERSION"] = get_config('api.azure.openai.api_version')

os.environ["EMBEDDING_AZURE_OPENAI_API_KEY"] = get_config('api.azure.embedding.api_key')
os.environ["EMBEDDING_AZURE_DEPLOYMENT"] = get_config('api.azure.embedding.azure_deployment')
os.environ["EMBEDDING_AZURE_ENDPOINT"] = get_config('api.azure.embedding.azure_endpoint')
os.environ["EMBEDDING_AZURE_API_VERSION"] = get_config('api.azure.embedding.api_version')

openai_config = {
    "llm": {  # LLM配置
        "provider": "openai",
        "config": {
            "model": "gpt-4-32k",
            "temperature": 0.1,
            "max_tokens": 2000,
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-ada-002",
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            # "url": "neo4j+s://localhost:7687",
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "12345678"
        }
    },
    "version": "v1.1"  # v1.1配置支持Graph
}

azure_config = {
    "llm": {  # LLM配置
        "provider": "azure_openai",
        "config": {
            "model": "gpt-4o-mini",
            "temperature": 0.1,
            "max_tokens": 2000,
            "azure_kwargs": {
                "azure_deployment": "",
                "api_version": "",
                "azure_endpoint": "",
                "api_key": ""
            },
        }
    },
    "embedder": {
        "provider": "azure_openai",
        "config": {
            "model": "text-embedding-ada-002",
            "azure_kwargs": {
                "api_version": "",
                "azure_deployment": "",
                "azure_endpoint": "",
                "api_key": ""
            }
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            # "url": "neo4j+s://localhost:7687",
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "12345678"
        }
    },
    "version": "v1.1"  # v1.1配置支持Graph
}

m = Memory.from_config(azure_config)

owner = "lixiang"

# m.add("我叫李响", user_id=owner)
# m.add("我喜欢吃面包", user_id=owner)
# m.add("我最喜欢吃的面包是我女朋友侯晓晴做的司康面包", user_id=owner)
# m.add("司康面包的售价一般为18元左右", user_id=owner)
# m.add("我有两只猫，一只叫荔枝，一只叫西瓜。", user_id=owner)
# m.add("荔枝是一只小母猫，西瓜是一只小公猫", user_id=owner)

# owner_memery = m.get_all(user_id=owner)
# print(owner_memery)  # ER数据 e.g. {'source': 'lixiang', 'relationship': 'has_girlfriend', 'target': '侯晓晴'}

# query = "李响的宠物"
# related_memories = m.search(query, user_id=owner)
# print(related_memories)
