from pydantic import BaseModel, Field, field_validator
from enum import StrEnum


VALID_OP = ["+","-","*","^"]

class ProcessingType(StrEnum):
    sync_processing = "sync"
    async_sqs = "sqs"
    async_celery = "celery"

class EvalSchema(BaseModel):
    evaluation : str
    op_precedence: str | None = VALID_OP

class ExpressionResult(BaseModel):
    expression: str
    result: list[EvalSchema] | None = None

class Expression(BaseModel):
    response_type: ProcessingType | None = ProcessingType.sync_processing
    expression: str
    @field_validator('expression')
    def validate_expression(cls, v):
        op_cnt = 0
        for c in v:
            if not c.isdigit():
                if c not in VALID_OP:
                    raise ValueError(f"Invalid op in expression: {v}")
                op_cnt += 1
                continue

            if not c.isdigit():
                raise ValueError(f"expression has to be combination of digit and operator : {v}")

        return v


class OperatorSchema(BaseModel):
    operators: list[str]

    @field_validator('operators')
    def validate_operators(cls, v):
        if v not in VALID_OP:
            raise ValueError(f"Invalid operator: {v}")
        return v


