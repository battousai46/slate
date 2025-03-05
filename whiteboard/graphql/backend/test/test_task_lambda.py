from backend.task_lambda import TaskCreateProcessor, table, TaskRetrieveProcessor, processor_factory, \
    TaskUpdateProcessor, prepare_dynamo_update_expression
from unittest.mock import patch, MagicMock


@patch.object(table, "put_item", return_value=True)
@patch("backend.task_lambda.boto3.resource", return_value=MagicMock())
def test_task_create_processor(boto_mock, table_mock):
    # test TaskCreateProcessor
    processor = processor_factory("createTask")
    assert isinstance(processor, TaskCreateProcessor) is True
    inp = {'title': 'Sample Task',
           'description': 'This is a sample task',
           'due_date': '2025-03-04T12:00:00Z',
           'status': 'TO_DO'}

    resp = processor.process(inp)
    assert resp.get("title") == "Sample Task"
    assert resp.get("status") == "TO_DO"

@patch.object(table, "get_item", return_value={"Item":{"id":"1","title":"test task"}})
@patch("backend.task_lambda.boto3.resource",return_value=MagicMock())
def test_task_retrieve_processor(boto_mock,table_mock):
    # test Retrival of task by TaskRetrieveProcessor
    processor = processor_factory("getTask")
    assert isinstance(processor, TaskRetrieveProcessor) is True

    resp = processor.process(dict({"id":1}))

    assert resp.get("Item")["title"] == "test task"

@patch.object(table, "update_item", return_value={"Attributes":{"id":"101","title":"test task"}})
@patch.object(table, "get_item", return_value={"Item":{"id":"101","title":"test task"}})
@patch("backend.task_lambda.boto3.resource",return_value=MagicMock())
def test_update_processor(boto_mock,table_mock,update_mock):
    # test update of task by TaskRetrieveProcessor
    processor = processor_factory("updateTask")
    assert isinstance(processor, TaskUpdateProcessor) is True
    resp = processor.process(dict({"id": "101", "title": "updated title", "status": "IN_PROGRESS"}))
    expected_response = {'id': '101', 'title': 'test task'}
    assert resp == expected_response


def test_prepare_update_statement():
    # test prepare update statement for dynamo
    inp = dict({"id": "101", "title": "updated title", "status": "IN_PROGRESS"})
    statement, names, values = prepare_dynamo_update_expression(inp)
    expected_statement = "SET #title = :title, #status = :status"
    expected_names = {'#title': 'title', '#status': 'status'}
    expected_values = {':title': 'updated title', ':status': 'IN_PROGRESS'}
    assert statement == expected_statement
    assert names == expected_names
    assert values == expected_values
