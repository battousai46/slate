import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from api.routes.v1.views import router_v1
from helper.logging_slate import get_logger
from argparse import ArgumentParser, Namespace

logger = get_logger(__name__)
def log_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"exception in request -> {request}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=dict(detail=str(exc))
    )

def build_api()->FastAPI:
    tags = [{"name":"slate_whiteboard"}]
    app = FastAPI(
        title="Whiteboard Slate",
        description="Whiteboard API for Slate",
        openapi_tags=tags,
        version="1.0.0",
    )
    app.include_router(router_v1)
    app.add_exception_handler(Exception, log_exception_handler)

    return app

def get_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--port",help="http port", type=int, default=8000)
    parser.add_argument("--host", help="http server host", type=str, default="0.0.0.0")
    parser.add_argument(
        "--workers",
        help="Number of workers to handle HTTP requests",
        type=int,
        default=1,
    )
    parser.add_argument("--reload", help="activate reload asgi loop", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    uvicorn.run(
        "bin.start_api:build_api",
        port=args.port,
        host=args.host,
        workers=args.workers,
        reload=args.reload,
    )