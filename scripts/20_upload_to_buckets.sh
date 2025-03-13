#!/bin/bash

# 04_upload_to_buckets.sh
# Uploads documentation to Google Cloud Storage buckets

# Exit on error
set -e

# Source environment variables
source .env

echo "=== Uploading documentation to Google Cloud Storage buckets ==="

# Function to upload files to a bucket
upload_to_bucket() {
    local source_dir=$1
    local bucket_name=$2
    
    echo "Uploading files from $source_dir to $bucket_name"
    
    if [ -d "$source_dir" ]; then
        gsutil -m cp -r "$source_dir/*" "$bucket_name/" || {
            echo "Warning: Upload to $bucket_name failed or partially failed. Continuing..."
        }
        echo "Uploaded files to $bucket_name"
    else
        echo "Directory $source_dir does not exist, skipping upload"
    fi
}

# Upload to datastore buckets
echo "Uploading to datastore buckets..."
for store in looker bigquery dbt gcp omni looker_studio; do
    bucket="${BUCKET_BASE%/}-${store}"
    upload_to_bucket "datastores/$store" "$bucket"
done

echo "=== Upload to buckets completed ==="
echo "You can now proceed to the next script: 05_create_datastores.sh" 