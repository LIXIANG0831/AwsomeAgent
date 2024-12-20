import subprocess
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from contextlib import asynccontextmanager
from settings import get_config
from core.init_app import init_database
from middleware import log_access


@asynccontextmanager
async def _LIFESPAN(app: FastAPI):
    # 初始化数据库
    init_database()

    # 启动 Celery worker
    # celery_command = f"celery -A awsome.core.celery_app worker --loglevel=info"  # 替换为你的模块路径
    # process = subprocess.Popen(celery_command, shell=True)

    yield  # yield 前为程序启动前 后为程序关闭后

    # 关闭 Celery worker
    # process.terminate()


_EXCEPTION_HANDLERS = {
    # 添加自定义异常处理器
}


def create_app():
    """Create the FastAPI app and include the router."""
    app = FastAPI(
        default_response_class=ORJSONResponse,
        exception_handlers=_EXCEPTION_HANDLERS,
        lifespan=_LIFESPAN,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.middleware("http")(log_access)

    from api.router import root_router
    app.include_router(root_router)

    return app


app = create_app()

if __name__ == '__main__':
    import uvicorn

    port = get_config("app.port")  # 运行端口
    uvicorn.run(app, host='0.0.0.0', port=port, workers=1)
