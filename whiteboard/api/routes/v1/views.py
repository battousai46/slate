from bin.eval_expr import evaluate_expression
from helper.logging_slate import get_logger
from common.config import get_current_config
from fastapi import APIRouter, Depends, status, Header, Request
from fastapi.responses import JSONResponse
from api.schema.eval_schema import Expression, ExpressionResult
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from jwt import encode
from datetime import datetime, timedelta
logger = get_logger(__name__)
current_config = get_current_config()

router_v1 = APIRouter(prefix="/v1")


def authenticated(req: Request):
    if req.user.is_authenticated:
        print(f"{req.user.username} logged in")
    return req.user.is_authenticated


@router_v1.get("/healthz", dependencies=[Depends(authenticated)])
def liveness_check():
    return JSONResponse({"env":current_config.ENV}, status_code=status.HTTP_200_OK)

@router_v1.get("/demo")
def demo_eval():
    return JSONResponse({"env":current_config.ENV}, status_code=status.HTTP_200_OK)


@router_v1.post("/eval")
def eval_expr(expr: Expression)->ExpressionResult:
    return evaluate_expression(expr)


@router_v1.post("/token")
async def login_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    print("---auth not implemented-- mocking")
    print(form_data.username)
    token_data = {"sub": form_data.username, "socpes": "read|write", "exp":datetime.now()+timedelta(hours=5)}
    encoded_jwt = encode(token_data,"super_secret",algorithm="HS256")
    return encoded_jwt