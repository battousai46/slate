from api.schema.eval_schema import Expression, ExpressionResult, EvalSchema
from helper.logging_slate import get_logger

logger = get_logger(__name__)

operations = [
    ("+", lambda a, b: a + b),
    ("-", lambda  a,b: a-b),
    ("*", lambda a, b: a * b),
    ("^", lambda a, b: pow(a, b)),
]

def calc( input_str , depth) :
      if depth >= len(operations):
          return float(input_str)
      split_op, split_operation = operations[depth]

      splitted_input = input_str.split(split_op)

      logger.info(f" {splitted_input}  depth  {depth}" )
      ret = calc( splitted_input[0], depth + 1)

      for each_ith in splitted_input[1:]:
          # 3 - 2 - 1
          next_val = calc( each_ith , depth + 1 )
          ret = split_operation(ret,next_val)

      return ret


def evaluate_expression(expr: Expression):
    result = [
        EvalSchema(
            evaluation=str(calc(expr.expression,0)),
        )

    ]
    ret =  ExpressionResult(expression=expr.expression, result=result )
    return ret

