import boto3
import json
# Configure the S3 client to use LocalStack's endpoin
s3_client = boto3.client('s3', endpoint_url='http://localhost:4566', region_name='us-east-1')

# bucket_name = 'raphql-datasource-lambda'
# zip_file = 'task_lambda.zip'
# object_name = 'task_lambda.zip'

def create_bucket(bucket_name):
    # Create bucket if it doesn't exist
    try:
        s3_client.create_bucket(Bucket=bucket_name)
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket {bucket_name} already exists.")

def upload_zip_file(zip_file, bucket_name, object_name):
    # Upload the ZIP file to S3
    s3_client.upload_file(zip_file, bucket_name, object_name)
    print(f"Uploaded {zip_file} to s3://{bucket_name}/{object_name}")


def invoke_lambda_mock():
    lambda_client = boto3.client('lambda', endpoint_url="http://localhost:4566")
    payload = {
        "key": "mock_payload_irfan",
    }
    response = lambda_client.invoke(
        FunctionName="TaskResolverLambda",
        Payload=json.dumps(payload)
    )
    print(response)
if __name__ == "__main__":
    bucket_name = 'graphql-datasource-lambda'
    zip_file = 'task_lambda.zip'
    object_name = 'task_lambda.zip'
    #upload_zip_file(zip_file, bucket_name, object_name)
    #invoke_lambda_mock()


