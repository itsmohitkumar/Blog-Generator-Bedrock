import boto3
import botocore.config
import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Constants (use environment variables or hardcode for now)
REGION_NAME = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("MODEL_ID", "meta.llama3-8b-instruct-v1:0")  # Updated model ID
S3_BUCKET = os.getenv("S3_BUCKET", "blog-generation-s3bucket")

# Boto3 clients
bedrock_client = boto3.client("bedrock-runtime", region_name=REGION_NAME,
                              config=botocore.config.Config(read_timeout=300, retries={'max_attempts': 3}))
s3_client = boto3.client('s3')

def blog_generate_using_bedrock(blog_topic):
    """Generate a blog using AWS Bedrock."""
    prompt = f"<s>[INST]Human: Write a 200-word blog on the topic: {blog_topic}\nAssistant:[/INST]"

    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9
    }

    logger.info(f"Invoking model with ID: {MODEL_ID}")
    logger.info(f"Request body: {json.dumps(body)}")

    try:
        response = bedrock_client.invoke_model(
            modelId=MODEL_ID,
            contentType='application/json',  # Set content type
            accept='application/json',        # Set accept type
            body=json.dumps(body)             # Convert body to JSON string
        )

        response_body = response['body'].read().decode('utf-8')
        response_json = json.loads(response_body)
        return response_json.get('generation', '')

    except Exception as e:
        logger.error(f"Error generating the blog: {e}")
        raise

def save_blog_details_s3(s3_key: str, blog_content: str) -> None:
    """Save the generated blog content to S3."""
    try:
        s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=blog_content)
        logger.info(f"Blog content saved to S3 at {s3_key}")

    except Exception as e:
        logger.error(f"Error when saving the blog to S3: {e}")
        raise

def lambda_handler(event, context):
    """Lambda function to handle blog generation and S3 upload."""
    try:
        # Log the incoming event to inspect the structure
        logger.info(f"Received event: {event}")

        # Check if the 'body' key exists in the event
        if 'body' not in event:
            raise ValueError("'body' key missing in event")

        event_body = json.loads(event['body'])
        blog_topic = event_body.get('blog_topic')
        
        if not blog_topic:
            raise ValueError("Blog topic is required.")

        generated_blog = blog_generate_using_bedrock(blog_topic)

        if generated_blog:
            current_time = datetime.now().strftime('%Y%m%d%H%M%S')
            s3_key = f"blog-output/{current_time}.txt"
            save_blog_details_s3(s3_key, generated_blog)
            response_body = "Blog generation and upload completed successfully."
        else:
            response_body = "Blog generation failed."

        return {
            'statusCode': 200,
            'body': json.dumps(response_body)
        }

    except Exception as e:
        logger.error(f"Error in Lambda handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal server error: {e}")
        }
