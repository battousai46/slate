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
    """
     event processor to handle single task creation
    """

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
            return {"task": valid_task, "error": None}
        # catching generic exception, better to catch specific
        except Exception as ex:
            print("exception in TaskCreateProcessor", str(ex))
            return {"task": None, "error": {"message": str(ex)}}


class TaskRetrieveProcessor(EventProcessor):
    """
     event processor to handle single task retrival
    """

    def process(self, args: dict) -> dict:
        try:
            task_id = args.get("id", None)
            if task_id is None:
                return {"task": None,
                        "error": {"message": f"{ERROR_TASK_ID_MISSING}"}}
            task = table.get_item(Key={"id": task_id})
            if task is None or task.get("Item") is None:
                return {"task": None,
                        "error": {"message": f"{ERROR_TASK_NOT_FOUND} for {task_id}"}}
            return {"task": task, "error": None}
        except Exception as ex:
            print("exception in TaskCreateProcessor", str(ex))
            return {"task": None, "error": {"message": str(ex)}}


class TaskUpdateProcessor(EventProcessor):
    """
      event processor to update task
    """

    def process(self, args: dict) -> dict:
        try:
            task_id = args.get("id", None)
            if task_id is None:
                return {"task": None,
                        "error": {"message": f"{ERROR_TASK_ID_MISSING}"}}

            # check arg has valid keys, though appsync resolver filters them
            valid_keys = Task.__annotations__.keys()
            invalid_keys = set(args.keys()) - set(valid_keys)
            if invalid_keys:
                return {"task": None, "error": {"message": f"Invalid attributes: {list(invalid_keys)}"}}

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
            updated_task = response.get("Attributes", {})
            return {"task": updated_task, "error": None}
        # TypeError, catch all exception instead
        except Exception as ex:
            print("exception in TaskUpdateProcessor", str(ex))
            return {"task": None, "error": {"message": str(ex)}}


class TaskDeleteProcessor(EventProcessor):
    """
      event processor to delete task
    """

    def process(self, args):
        try:
            task_id = args.get("id")
            if not task_id:
                return {"task": None, "error": {"message": ERROR_TASK_ID_MISSING}}

            deleted_item = table.delete_item(
                Key={"id": task_id},
                ReturnValues="ALL_OLD"
            )
            deleted_task = deleted_item.get("Attributes")
            if deleted_task is None:
                return {"task": None, "error": {"message": f"{ERROR_TASK_NOT_FOUND} with ID {task_id}"}}

            return {"task": deleted_task, "error": None}
        except Exception as ex:
            print("exception in TaskDeleteProcessor", str(ex))
            return {"task": None, "error": {"message": str(ex)}}


class TaskListProcessor(EventProcessor):
    """
    event processor to retrieve list of tasks, paginated by limit and next token
    """

    def process(self, args):
        # paginated by limit and token
        try:
            limit = int(args.get("limit", 10))
            next_token = args.get("nextToken", None)
            table_scan_params = {
                "Limit": limit
            }
            if next_token:
                prev_key = json.loads(next_token)
                table_scan_params["ExclusiveStartKey"] = prev_key

            data = table.scan(**table_scan_params)
            next_token = data.get("LastEvaluatedKey", None)
            if next_token:
                next_token = json.dumps(next_token)

            tasks = []
            for item in data.get("Items", []):
                tasks.append({"id": item["id"],
                              "title": item["title"],
                              "status": item["status"]})

            return {
                "tasks": tasks,
                "nextToken": next_token,
                "error": None
            }

        except Exception as ex:
            print("exception in TaskListProcessor", str(ex))
            return {"tasks": None, "nextToken": None, "error": {"message": str(ex)}}


class UnknownTaskProcessor(EventProcessor):
    def process(self, args: dict) -> dict:
        return {"task": None,
                "error": {"message": "Unknown task event"}}


def processor_factory(event_type):
    match event_type:
        case "createTask":
            return TaskCreateProcessor()
        case "updateTask":
            return TaskUpdateProcessor()
        case "deleteTask":
            return TaskDeleteProcessor()
        case "getTask":
            return TaskRetrieveProcessor()
        case "listTask":
            return UnknownTaskProcessor()
        case _:
            return UnknownTaskProcessor()  # UnknownTaskProcessor()


def handler(event, context):
    print("event details:", json.dumps(event))
    try:
        field = event.get("field")
        processor = processor_factory(field)
        args = event.get("arguments")
        print(f"fields {field} and arguments {args}")
        response = processor.process(args)
        print(f"response {response}")
        return response
    # TODO should filterout generic exception
    except Exception as ex:
        print("exception in handler ", str(ex))
        return {"task": None, "error": {"message": str(ex)}}
