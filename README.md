# Blog Generation with AWS Bedrock

## Overview

This project is an AWS Lambda function that leverages the `meta.llama3-8b-instruct-v1:0` model from AWS Bedrock to generate blog content based on user-defined topics. The generated content is then saved to an Amazon S3 bucket for easy access and management. The function supports customizable blog lengths, keyword inclusion for SEO, and generates metadata for each blog post.

## Features

- **Blog Generation**: Generate high-quality blog posts on various topics.
- **Customizable Lengths**: Users can specify the desired length of the blog post (e.g., 200 words, 500 words).
- **SEO Optimization**: Include keywords in the blog for better search engine visibility.
- **Metadata Tracking**: Automatically saves metadata such as blog topic, generation timestamp, and summary.
- **AWS Integration**: Seamlessly integrates with AWS Bedrock for model invocation and S3 for storage.
- **Logging**: Provides comprehensive logging for debugging and monitoring.

## Requirements

- **AWS Account**: You must have an active AWS account with access to AWS Bedrock and S3.
- **IAM Role**: Ensure you have an IAM role with the necessary permissions to invoke Bedrock models and access S3.
- **Python Version**: The code is compatible with Python 3.x.

## Installation

Follow these steps to set up the project locally:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/itsmohitkumar/blog-generation-bedrock
   cd blog-generation-bedrock
   ```

2. **Create a Virtual Environment (optional but recommended)**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows use `venv\Scripts\activate`
   ```

3. **Install Required Packages**:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables

Before running the Lambda function, set the following environment variables:

- **`AWS_REGION`**: The AWS region where your services are located (default: `us-east-1`).
- **`MODEL_ID`**: The ID of the Bedrock model to use for blog generation (default: `meta.llama3-8b-instruct-v1:0`).
- **`S3_BUCKET`**: The name of the S3 bucket where the generated blog content will be stored (default: `blog-generation-s3bucket`).

### IAM Permissions

Make sure your Lambda function has the following IAM permissions:

- **`bedrock:InvokeModel`**: Required to invoke the Bedrock model.
- **`s3:PutObject`**: Required to save objects to the specified S3 bucket.

## Usage

### Event Format

The Lambda function expects an event in the following JSON format:

```json
{
    "body": "{\"blog_topic\": \"Your Blog Topic Here\", \"blog_length\": 200, \"keywords\": [\"keyword1\", \"keyword2\"]}"
}
```

### Example Event

Here’s an example of how to structure your event for testing:

```json
{
    "body": "{\"blog_topic\": \"The Future of Artificial Intelligence\", \"blog_length\": 300, \"keywords\": [\"AI\", \"technology\"]}"
}
```

## Deployment

You can deploy the Lambda function using the AWS Management Console or the AWS CLI. Ensure that the correct environment variables are configured in the Lambda settings.

### Deploying with AWS CLI

1. Package your application:

   ```bash
   zip -r function.zip .  # Assumes you are in the root of your project directory
   ```

2. Create or update the Lambda function:

   ```bash
   aws lambda create-function --function-name BlogGenerationFunction \
     --zip-file fileb://function.zip --handler <your_handler_file>.lambda_handler \
     --runtime python3.x --role <your_execution_role_arn> \
     --environment AWS_REGION=us-east-1,MODEL_ID=meta.llama3-8b-instruct-v1:0,S3_BUCKET=blog-generation-s3bucket
   ```

## Logging

The Lambda function logs key events and errors. You can view the logs in **Amazon CloudWatch Logs** for monitoring and debugging purposes.

## Contributing

Contributions are welcome! If you have suggestions or improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [AWS Documentation](https://docs.aws.amazon.com/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
