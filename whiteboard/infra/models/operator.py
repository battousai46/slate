from infra.models.base import BaseModel
from sqlmodel import Field, Relationship
from typing import List

class OperatorPrecedence(BaseModel, table=True):
      op_precedence: str
      #eval_results: List["EvalResult"] #= Relationship(back_populates="operator_precedence")


class ApiTask(BaseModel, table=True):
    task_id: str
    subscriber: str | None = None


class EvalResult(BaseModel, table=True):
    expression: str
    #operator_id: Field(foreign_key="operator_precedence.id",index=True)
    #operator: OperatorPrecedence #= Relationship(back_populates="eval_results")
