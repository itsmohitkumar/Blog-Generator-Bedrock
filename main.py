import boto3
import botocore.config
import json
from datetime import datetime

def quote_generate_using_bedrock(topic: str) -> str:
    """Generates a quote using Bedrock."""
    
    prompt = f"""<s>[INST]Human: Provide a motivational quote on the topic "{topic}".
    Assistant:[/INST]
    """
    
    body = {
        "prompt": prompt,
        "max_gen_len": 128,  # Reduced length since quotes are shorter
        "temperature": 0.7,  # Slightly increased for more creative outputs
        "top_p": 0.9
    }

    try:
        bedrock = boto3.client(
            "bedrock-runtime", 
            region_name="us-east-1",
            config=botocore.config.Config(
                read_timeout=300, 
                retries={'max_attempts': 3}
            )
        )
        response = bedrock.invoke_model(
            body=json.dumps(body), 
            modelId="meta.llama2-13b-chat-v1"
        )

        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        quote = response_data.get('generation', '')
        
        if quote:
            return quote
        else:
            raise ValueError("No quote content in the response.")
    
    except Exception as e:
        print(f"Error generating the quote: {e}")
        return ""

def save_quote_to_s3(s3_key: str, s3_bucket: str, quote: str) -> None:
    """Saves the generated quote to an S3 bucket."""
    
    s3 = boto3.client('s3')

    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=quote)
        print("Quote saved to S3 successfully.")
    
    except Exception as e:
        print(f"Error saving the quote to S3: {e}")

def lambda_handler(event, context):
    """AWS Lambda handler to generate a quote and save it to S3."""
    
    try:
        event_data = json.loads(event['body'])
        topic = event_data['topic']  # Changed key to reflect quote topic
        
        generated_quote = quote_generate_using_bedrock(topic=topic)

        if generated_quote:
            current_time = datetime.now().strftime('%H%M%S')
            s3_key = f"quote-output/{current_time}.txt"
            s3_bucket = 'aws_bedrock_course1'
            
            save_quote_to_s3(s3_key, s3_bucket, generated_quote)
        
        else:
            print("No quote was generated.")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Quote generation completed successfully.')
        }

    except KeyError as e:
        print(f"Key error: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps(f"Invalid input data: {e}")
        }
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('An error occurred during quote generation.')
        }
