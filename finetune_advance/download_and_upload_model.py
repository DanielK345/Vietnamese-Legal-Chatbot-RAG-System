#!/usr/bin/env python3
"""
Script to download model from Digital Ocean Spaces and upload to Hugging Face
"""

import os
import boto3
from botocore.client import Config
from pathlib import Path
from huggingface_hub import HfApi, create_repo
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Digital Ocean Spaces configuration
DO_SPACE_NAME = "legal-datalake"
DO_REGION = "sfo3"  # Change this to your region (sgp1, nyc3, sfo3, etc.)
DO_ENDPOINT = f"https://{DO_REGION}.digitaloceanspaces.com"
MODEL_PATH_IN_BUCKET = "models/vietnamese-legal-llama-20251111_115138"

# Hugging Face configuration
HF_REPO_ID = "mikeethanh/vietnamese_legal_llama"

# Local paths
LOCAL_MODEL_DIR = "./downloaded_model"


def download_from_digital_ocean():
    """Download model from Digital Ocean Spaces"""
    logger.info("Starting download from Digital Ocean Spaces...")
    
    # Get credentials from environment variables
    access_key = os.getenv("DO_SPACES_ACCESS_KEY")
    secret_key = os.getenv("DO_SPACES_SECRET_KEY")
    
    if not access_key or not secret_key:
        raise ValueError(
            "Please set DO_SPACES_ACCESS_KEY and DO_SPACES_SECRET_KEY environment variables"
        )
    
    # Initialize S3 client for Digital Ocean Spaces
    session = boto3.session.Session()
    client = session.client(
        's3',
        region_name=DO_REGION,
        endpoint_url=DO_ENDPOINT,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version='s3v4')
    )
    
    # Create local directory
    os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)
    
    # List all files in the model directory
    logger.info(f"Listing files in {MODEL_PATH_IN_BUCKET}...")
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=DO_SPACE_NAME, Prefix=MODEL_PATH_IN_BUCKET)
    
    files_downloaded = 0
    for page in pages:
        if 'Contents' not in page:
            logger.warning(f"No files found in {MODEL_PATH_IN_BUCKET}")
            break
            
        for obj in page['Contents']:
            file_key = obj['Key']
            
            # Skip if it's a directory marker
            if file_key.endswith('/'):
                continue
            
            # Create local file path
            relative_path = file_key.replace(MODEL_PATH_IN_BUCKET, '').lstrip('/')
            local_file_path = os.path.join(LOCAL_MODEL_DIR, relative_path)
            
            # Create subdirectories if needed
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            
            # Download file
            logger.info(f"Downloading {file_key} to {local_file_path}...")
            client.download_file(DO_SPACE_NAME, file_key, local_file_path)
            files_downloaded += 1
    
    logger.info(f"Successfully downloaded {files_downloaded} files to {LOCAL_MODEL_DIR}")
    return LOCAL_MODEL_DIR


def upload_to_huggingface(model_dir):
    """Upload model to Hugging Face Hub"""
    logger.info("Starting upload to Hugging Face...")
    
    # Get token from environment variable
    hf_token = os.getenv("HF_TOKEN")
    
    if not hf_token:
        raise ValueError("Please set HF_TOKEN environment variable")
    
    # Initialize Hugging Face API
    api = HfApi()
    
    # Create repository if it doesn't exist
    try:
        logger.info(f"Creating repository {HF_REPO_ID}...")
        create_repo(
            repo_id=HF_REPO_ID,
            token=hf_token,
            private=False,
            exist_ok=True
        )
    except Exception as e:
        logger.warning(f"Repository creation note: {e}")
    
    # Upload all files from the model directory
    logger.info(f"Uploading files from {model_dir} to {HF_REPO_ID}...")
    api.upload_folder(
        folder_path=model_dir,
        repo_id=HF_REPO_ID,
        token=hf_token,
        commit_message="Upload Vietnamese Legal LLaMA model from Digital Ocean"
    )
    
    logger.info(f"Successfully uploaded model to https://huggingface.co/{HF_REPO_ID}")


def main():
    """Main execution function"""
    try:
        # Step 1: Download from Digital Ocean
        model_dir = download_from_digital_ocean()
        
        # Step 2: Upload to Hugging Face
        upload_to_huggingface(model_dir)
        
        logger.info("Process completed successfully!")
        
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
