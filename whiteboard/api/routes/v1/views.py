from bin.eval_expr import evaluate_expression
from helper.logging_slate import get_logger
from common.config import get_current_config
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from api.schema.eval_schema import Expression, ExpressionResult

logger = get_logger(__name__)
current_config = get_current_config()

router_v1 = APIRouter(prefix="/v1")

@router_v1.get("/healthz")
def liveness_check():
    return JSONResponse({"env":current_config.ENV}, status_code=status.HTTP_200_OK)

@router_v1.get("/demo")
def demo_eval():
    return JSONResponse({"env":current_config.ENV}, status_code=status.HTTP_200_OK)


@router_v1.post("/eval")
def eval_expr(expr: Expression)->ExpressionResult:
    return evaluate_expression(expr)
