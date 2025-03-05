from __future__ import annotations
import json
import os
import uuid
import boto3
from typing import Protocol
from abc import abstractmethod
from dataclasses import dataclass, field, asdict
from enum import StrEnum
from typing import Optional
from datetime import datetime


# load environment variable
AWS_REGION = os.environ.get('AWS_REGION', "ap-southeast-2")
TASKS_TABLE = os.environ.get("TASKS_TABLE", "Tasks")
DYNAMODB_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT", )
# init dynamodb in coldstart, reduced retry
dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    endpoint_url=os.getenv("DYNAMODB_ENDPOINT", "http://host.docker.internal:4566")
    # Ensure compatibility inside Docker
)

table = dynamodb.Table(TASKS_TABLE)

# CONSTANTS_LITERALS
ERROR_TASK_ID_MISSING = "No Task ID provided"
ERROR_TASK_NOT_FOUND = "Task not found"


class TaskStatus(StrEnum):
    IN_PROGRESS = "IN_PROGRESS"
    TO_DO = "TO_DO"
    COMPLETED = "COMPLETED"


@dataclass
class Task:
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = field(default=TaskStatus.TO_DO)
    description: Optional[str] = field(default=None)
    due_date: Optional[datetime] = field(default=None)


# utils
def prepare_dynamo_update_expression(task_to_update: dict):
    """
    prepare update statement, expression name and values
    for dynamodb update boto3 update
    """
    # init defaultdict(str)
    expr_values = {}
    expr_names = {}
    update_expr = "SET "

    for key, value in task_to_update.items():
        if key == "id":
            continue
        update_expr += f"#{key} = :{key}, "
        expr_names[f"#{key}"] = key
        expr_values[f":{key}"] = value

    # added trailing spaces before, remove afterwards
    update_expr = update_expr.rstrip(", ")
    return update_expr, expr_names, expr_values


class EventProcessor(Protocol):
    """
    processor to handle events
    """

    @abstractmethod
    def process(self, event: dict) -> dict:
        """
        process event based on type { Mutation, Query }
        """


class TaskCreateProcessor(EventProcessor):
    # handle task creation event
    def process(self, args: dict) -> dict:
        try:
            task = Task(
                id=str(uuid.uuid4()),
                title=args.get("title"),
                description=args.get("description", ""),
                status=args.get("status", TaskStatus.TO_DO),
                due_date=args.get("due_date", None)
            )
            valid_task = asdict(task)
            table.put_item(Item=valid_task)
            return valid_task
        # catching generic exception, better to catch specific
        except Exception as ex:
            print("exception in TaskCreateProcessor", str(ex))
            return {"error": str(ex)}


class TaskRetrieveProcessor(EventProcessor):
    def process(self, args: dict) -> dict:
        try:
            task_id = args.get("id", None)
            if task_id is None:
                return {"error": ERROR_TASK_ID_MISSING}
            task = table.get_item(Key={"id": task_id})
            if task is None or task.get("Item") is None:
                return {"error": f"{ERROR_TASK_NOT_FOUND} for {task_id}"}
            return task
        except Exception as ex:
            print("exception in TaskCreateProcessor", str(ex))
            return {"error": str(ex)}


class TaskUpdateProcessor(EventProcessor):
    def process(self, args: dict) -> dict:
        try:
            task_id = args.get("id", None)
            if task_id is None:
                return {"error": ERROR_TASK_ID_MISSING}

            # check arg has valid keys, though appsync resolver filters them
            valid_keys = Task.__annotations__.keys()
            invalid_keys = set(args.keys()) - set(valid_keys)
            if invalid_keys:
                return {"error": f"invalid attributes {invalid_keys}"}

            # get task
            task = TaskRetrieveProcessor().process(args)
            if "error" in task:
                return task

            expr_statement, expr_names, expr_values = prepare_dynamo_update_expression(args)

            response = table.update_item(
                Key={"id": task_id},
                UpdateExpression=expr_statement,
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_values,
                ReturnValues="ALL_NEW"
            )

            return response.get("Attributes", {})
        # TypeError, catch all exception instead
        except Exception as ex:
            print("exception in TaskUpdateProcessor", str(ex))
            return {"error": str(ex)}


class UnknownTaskProcessor(EventProcessor):
    def process(self, args: dict) -> dict:
        return {"error": "Unknown task event"}


def processor_factory(event_type):
    match event_type:
        case "createTask":
            return TaskCreateProcessor()
        case "updateTask":
            return TaskUpdateProcessor()
        case "deleteTask":
            return UnknownTaskProcessor()  # TaskDeleteProcessor()
        case "getTask":
            return TaskRetrieveProcessor()
        case _:
            return UnknownTaskProcessor()  # UnknownTaskProcessor()


def handler(event, context):
    print("event details:", json.dumps(event))
    try:
        field = event.get("field")
        processor = processor_factory(field)
        args = event.get("arguments")
        print(f"fields {field} and arguments {args}")
        return processor.process(args)

    # TODO should filterout generic exception
    except Exception as ex:
        print("exception in handler ", str(ex))
        return {"error": str(ex)}
