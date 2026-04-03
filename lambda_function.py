import boto3
import os
import json
from botocore.config import Config

def lambda_handler(event, context):
    print("EVENT =", event)

    config = Config(connect_timeout=2, read_timeout=2, retries={'max_attempts': 0})

    ec2 = boto3.client(
        "ec2",
        endpoint_url="http://localhost.localstack.cloud:4566",
        region_name="us-east-1",
        config=config
    )

    instance_id = os.environ.get("INSTANCE_ID")

    # 🔥 gestion propre des cas
    try:
        if "body" in event:
            body = json.loads(event["body"])
        else:
            body = event
    except Exception as e:
        return {"error": f"Invalid JSON: {str(e)}"}

    action = body.get("action", "start")

    if not instance_id:
        return {"error": "INSTANCE_ID missing"}

    try:
        if action == "start":
            ec2.start_instances(InstanceIds=[instance_id])
            return {"status": "started"}

        elif action == "stop":
            ec2.stop_instances(InstanceIds=[instance_id])
            return {"status": "stopped"}

    except Exception as e:
        return {"error": str(e)}

    return {"status": "unknown"}