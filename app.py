import boto3
import botocore.config
import json
import os
import logging
from datetime import datetime
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Constants (use environment variables or hardcode for now)
REGION_NAME = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("MODEL_ID", "meta.llama3-8b-instruct-v1:0")  # Model ID
S3_BUCKET = os.getenv("S3_BUCKET", "blog-generation-s3bucket")

# Boto3 clients
bedrock_client = boto3.client("bedrock-runtime", region_name=REGION_NAME,
                              config=botocore.config.Config(read_timeout=900, retries={'max_attempts': 3}))
s3_client = boto3.client('s3')

def extract_blog_topic(event):
    """Extract and validate the blog topic from the event."""
    if 'body' not in event:
        raise ValueError("'body' key missing in event")
    event_body = json.loads(event['body'])
    blog_topic = event_body.get('blog_topic')
    if not blog_topic or len(blog_topic) < 3:
        raise ValueError("Blog topic must be at least 3 characters long.")
    return blog_topic, event_body

def blog_generate_using_bedrock(blog_topic, blog_length=200, keywords=None):
    """Generate a blog using AWS Bedrock with optional length and keywords."""
    prompt = f"<s>[INST]Human: Write a {blog_length}-word blog on the topic: {blog_topic}\nAssistant:[/INST]"

    if keywords:
        prompt += f" Make sure to include the following keywords: {', '.join(keywords)}."

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
            contentType='application/json',
            accept='application/json',
            body=json.dumps(body)
        )
        response_body = response['body'].read().decode('utf-8')
        response_json = json.loads(response_body)
        return response_json.get('generation', '')

    except ClientError as e:
        logger.error(f"ClientError during model invocation: {e}")
        raise
    except Exception as e:
        logger.error(f"Error generating the blog: {e}")
        raise

def save_blog_details_s3(s3_key: str, blog_content: str, metadata: dict) -> None:
    """Save the generated blog content and metadata to S3."""
    try:
        # Save blog content
        s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=blog_content)
        logger.info(f"Blog content saved to S3 at {s3_key}")

        # Save metadata
        metadata_key = f"{s3_key}_metadata.json"
        s3_client.put_object(Bucket=S3_BUCKET, Key=metadata_key, Body=json.dumps(metadata))
        logger.info(f"Metadata saved to S3 at {metadata_key}")

    except ClientError as e:
        logger.error(f"ClientError during S3 upload: {e}")
        raise
    except Exception as e:
        logger.error(f"Error when saving the blog to S3: {e}")
        raise

def generate_blog_summary(blog_content):
    """Generate a summary of the generated blog using the model."""
    prompt = f"<s>[INST]Human: Summarize the following blog:\n{blog_content}\nAssistant:[/INST]"

    body = {
        "prompt": prompt,
        "max_gen_len": 100,
        "temperature": 0.5,
        "top_p": 0.9
    }

    try:
        response = bedrock_client.invoke_model(
            modelId=MODEL_ID,
            contentType='application/json',
            accept='application/json',
            body=json.dumps(body)
        )
        response_body = response['body'].read().decode('utf-8')
        response_json = json.loads(response_body)
        return response_json.get('generation', '')

    except ClientError as e:
        logger.error(f"ClientError during summary generation: {e}")
        raise
    except Exception as e:
        logger.error(f"Error generating the summary: {e}")
        raise

def lambda_handler(event, context):
    """Lambda function to handle blog generation and S3 upload."""
    try:
        logger.info(f"Received event: {event}")

        # Extract blog topic and optional length/keywords
        blog_topic, event_body = extract_blog_topic(event)
        blog_length = event_body.get('blog_length', 200)
        keywords = event_body.get('keywords', [])

        # Generate blog
        generated_blog = blog_generate_using_bedrock(blog_topic, blog_length, keywords)

        if generated_blog:
            # Generate blog summary
            summary = generate_blog_summary(generated_blog)

            # Prepare metadata
            current_time = datetime.now().strftime('%Y%m%d%H%M%S')
            s3_key = f"blog-output/{current_time}.txt"
            metadata = {
                "blog_topic": blog_topic,
                "generated_at": current_time,
                "blog_length": blog_length,
                "keywords": keywords,
                "summary": summary,
                "s3_key": s3_key
            }

            # Save blog and metadata to S3
            save_blog_details_s3(s3_key, generated_blog, metadata)
            
            response_body = {
                "message": "Blog generation and upload completed successfully.",
                "s3_link": f"s3://{S3_BUCKET}/{s3_key}",
                "metadata": metadata
            }

        else:
            response_body = {
                "message": "Blog generation failed.",
                "s3_link": None,
                "metadata": {}
            }

        return {
            'statusCode': 200,
            'body': json.dumps(response_body)
        }

    except Exception as e:
        logger.error(f"Error in Lambda handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                "message": "Internal server error",
                "error": str(e)
            })
        }
