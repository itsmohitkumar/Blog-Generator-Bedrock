# AWS Lambda: Install and Package boto3

This guide explains how to install `boto3` and package it into a zip file suitable for uploading to AWS Lambda.

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Installation Steps](#installation-steps)
- [Creating the Zip File](#creating-the-zip-file)
- [Uploading to AWS Lambda](#uploading-to-aws-lambda)
- [Cleaning Up](#cleaning-up)

## Overview

AWS Lambda does not include the latest version of `boto3` by default. This guide will help you install `boto3` and its dependencies locally, package them in a zip file, and upload the package to Lambda to ensure your function uses the latest `boto3` version.

## Requirements

Make sure you have the following installed on your machine:
- Python (version 3.x)
- Pip (Python package manager)

## Installation Steps

1. **Create a Directory for the Lambda Layer**
   
   To install `boto3` in a format that is compatible with AWS Lambda, we will install it in a folder named `python/`.

   Run the following command to install `boto3` into the `python/` directory:

   ```bash
   pip install boto3 -t python/
   ```

2. **Verify Installation**

   After running the above command, the `python/` directory will contain all `boto3` files and its dependencies. You can check the contents of the directory to ensure everything is installed correctly:

   ```bash
   ls python/
   ```

## Creating the Zip File

Once `boto3` is installed, we need to package the contents of the `python/` folder into a zip file that can be uploaded to AWS Lambda.

Run the following Python script to automate this process:

```python
import os
import zipfile
import shutil

# Zip file name
zip_file_name = 'boto3_lambda_package.zip'

# Create the zip file with the contents of the 'python' directory
with zipfile.ZipFile(zip_file_name, 'w') as lambda_zip:
    for folder_name, subfolders, filenames in os.walk('python'):
        for filename in filenames:
            file_path = os.path.join(folder_name, filename)
            lambda_zip.write(file_path, os.path.relpath(file_path, 'python'))

# Clean up by removing the 'python' directory
shutil.rmtree('python')

print(f"{zip_file_name} created successfully.")
```

This will create a zip file named `boto3_lambda_package.zip`.

## Uploading to AWS Lambda

To update your Lambda function with the latest version of `boto3`:

1. Log in to the [AWS Management Console](https://aws.amazon.com/console/).
2. Navigate to **AWS Lambda**.
3. Choose your Lambda function.
4. Under the **Code** section, click **Upload** and select the `boto3_lambda_package.zip` file you created.
5. Save the changes.

Once the upload is complete, your Lambda function will have access to the latest `boto3` package.

## Cleaning Up

After uploading the zip file, you may want to delete the local `python/` directory to clean up your working environment.

If you haven’t already, the script provided in the previous step will automatically remove the `python/` directory after creating the zip file.

You can manually remove the directory by running:

```bash
rm -rf python/
```

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute this project as per the terms of the license.

For more details, refer to the LICENSE file.
