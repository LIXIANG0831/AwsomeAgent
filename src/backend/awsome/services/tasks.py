from awsome.core.celery_app import celery as ywjz_celery
from awsome.models.dao.knowledge_file import KnowledgeFile
from awsome.models.schemas.es.save_document import SaveDocument
from awsome.models.v1.knowledge_file import KnowledgeFileVectorizeTasks
from awsome.utils.elasticsearch_util import ElasticSearchUtil
from awsome.utils.milvus_util import MilvusUtil
from awsome.utils.minio_util import MinioUtil
from awsome.utils.logger_util import logger_util
from awsome.utils.model_factory import ModelFactory
from awsome.utils.tools import PdfExtractTool
from awsome.services.constant import (milvus_default_fields_768,  # 默认字段
                                      milvus_default_index_params  # 默认索引配置
                                      )
from awsome.services.knowledge_file import KnowledgeFileService


@ywjz_celery.task(
    bind=True,
    autoretry_for=(Exception,),  # 自动重试所有异常
    max_retries=3,               # 最大重试次数
    retry_backoff=True,          # 启用退避策略
    retry_backoff_max=30,        # 最大重试间隔为 30 秒
    retry_backoff_factor=2       # 退避因子为 2
)
def celery_text_vectorize(self, task_json):
    knowledge_file_vectorize_task = KnowledgeFileVectorizeTasks.parse_obj(task_json)
    file_vectorize_err_msg = ""  # 记录异常信息
    try:
        # 实例化minio_client
        minio_client = MinioUtil()
        # 实例化milvus
        milvus_client = MilvusUtil()
        # 实例化es
        es_client = ElasticSearchUtil()
        # 获取默认模型配置客户端
        client = ModelFactory.create_client(embedding_name=knowledge_file_vectorize_task.embedding_name)
    except Exception as e:
        file_vectorize_err_msg += f"实例化异常:{e}\n"
        logger_util.exception(file_vectorize_err_msg)
        return  # 如果实例化失败，直接返回

    target_kb_id = knowledge_file_vectorize_task.target_kb_id  # target_knowledge_id
    target_collection_name = knowledge_file_vectorize_task.collection_name  # milvus_collection_name
    target_index_name = knowledge_file_vectorize_task.index_name  # es_index_name
    enable_layout_flag = knowledge_file_vectorize_task.enable_layout  # 是否开启布局识别
    for file_info in knowledge_file_vectorize_task.file_info_list:
        file_save_path = file_info["file_save_path"]
        file_name = file_info["file_name"]
        file_id = file_info["file_id"]
        file_object_name = file_info["file_object_name"]
        logger_util.debug(f"====》开始向量化文件{file_name}")
        try:
            if file_save_path == "": raise Exception("文件下载失败")
            # TODO 没有对separator进行支持

            # 文档切片向量化 组织数据结构
            extract_results = []
            if enable_layout_flag == 1:  # 布局识别
                # TODO 启用布局识别
                pass
            elif enable_layout_flag == 0:  # 不进行布局识别
                # 实例化pdf工具
                pdf_extractor = PdfExtractTool(file_save_path,
                                               chunk_size=knowledge_file_vectorize_task.chunk_size,
                                               repeat_size=knowledge_file_vectorize_task.repeat_size)
                extract_results = pdf_extractor.extract()  # pdf切片结果返回

            """
            插入ES
                - metadata
                    bbox | start_page[chunk片段最小页码] | source | title | chunk_index[分片索引] | extra | file_id | knowledge_id
                - text
            """
            for extra_result in extract_results:
                save_document = SaveDocument()

                save_document.index_name = target_index_name  # ***设置索引名称
                # chunk
                save_document.text = extra_result.get("chunk", "")
                save_document.metadata.bbox = extra_result.get("chunk_bboxes", "")
                save_document.metadata.start_page = extra_result.get("start_page", 0)
                save_document.metadata.source = file_object_name
                save_document.metadata.title = file_name
                save_document.metadata.chunk_index = extra_result.get("chunk_index", 0)
                save_document.metadata.extra = ""
                save_document.metadata.file_id = file_id
                save_document.metadata.knowledge_id = target_kb_id

                # 创建索引
                es_client.save_document(save_document)
            logger_util.debug("====》ES插入完成")
            """
            插入Milvus
            bbox | start_page[chunk片段最小页码] | source | title | chunk_index[分片索引] | extra | file_id | knowledge_id | text | vector | pk[auto_id]
            """
            if not milvus_client.check_collection_exists(target_collection_name):
                logger_util.debug(f"新建集合{target_index_name}")
                milvus_client.create_collection(target_collection_name, milvus_default_fields_768)
                logger_util.debug(f"完成集合{target_index_name}新建")
            # milvus 插入数据
            insert_data = []
            for m_extract_result in extract_results:
                chunk_vector_resp = client.get_embeddings(inputs=m_extract_result.get("chunk", ""))
                chunk_vector = chunk_vector_resp.data[0].embedding
                data = {
                    "bbox": str(m_extract_result.get("chunk_bboxes", "")),
                    "start_page": m_extract_result.get("start_page", 0),
                    "source": file_object_name,
                    "title": file_name,
                    "chunk_index": m_extract_result.get("chunk_index", 0),
                    "extra": "",
                    "file_id": file_id,
                    "knowledge_id": target_kb_id,
                    # title + chunk
                    "text": file_name + ":" + m_extract_result.get("chunk", ""),
                    # 调用Embedding模型获取向量数据
                    "vector": chunk_vector
                }
                insert_data.append(data)

            milvus_client.insert_data(target_collection_name, insert_data)
            # Desperate----- 创建Collection时已完成索引创建
            # milvus_client.create_index_on_field(target_collection_name, "vector", milvus_default_index_params)
            logger_util.debug("====》Milvus插入完成")

            # 完成向量化修改状态
            update_file: KnowledgeFile = KnowledgeFileService.select_by_file_id(file_id)[0]
            update_file.status = 1
            KnowledgeFileService.update_file(update_file)
            logger_util.debug("====》数据库数据更新状态")
        except Exception as e:
            logger_util.error(f"任务失败，正在重试，重试次数：{self.request.retries}")

            file_vectorize_err_msg += f"文件{file_name}解析异常:{e}\n"

            # 回写异常信息
            update_file: KnowledgeFile = KnowledgeFileService.select_by_file_id(file_id)[0]
            update_file.status = -1
            update_file.extra = file_vectorize_err_msg
            KnowledgeFileService.update_file(update_file)
            logger_util.info("====》解析异常数据库更新状态")

            file_vectorize_err_msg = ""  # 清除错误信息
            logger_util.exception(file_vectorize_err_msg)

            continue  # 跳过本次
