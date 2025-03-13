#!/bin/bash

# Flatten existing repository script
# This script takes repositories that are already cloned and flattens them
# into a single directory with unique filenames.

# Exit on error
set -e

# Configuration
ROOT_DIR="/Users/dionedge/dev/looker-vertex-agent"
LOG_FILE="$ROOT_DIR/flatten_existing_repos.log"

# Initialize log file
echo "Repository flattening process started at $(date)" > "${LOG_FILE}"

# Function to sanitize filename
sanitize_filename() {
    echo "$1" | sed 's/[^a-zA-Z0-9._-]/_/g'
}

# Function to flatten a directory
flatten_directory() {
    local source_dir="$1"
    local target_dir="$2"
    local repo_name="$3"
    
    echo "Flattening repository $repo_name from $source_dir to $target_dir"
    
    # Create target directory if it doesn't exist
    mkdir -p "${target_dir}"
    
    # Find all files (excluding .git directory and other hidden files)
    find "${source_dir}" -type f -not -path '*/\.*' -not -path '*/node_modules/*' -not -path '*/venv/*' | while read -r file; do
        # Get the original filename
        filename=$(basename "$file")
        
        # Get the relative path from the source directory
        rel_path=${file#$source_dir/}
        
        # Replace directory separators with underscores
        flat_name=$(echo "${repo_name}_${rel_path}" | tr '/' '_')
        
        # Sanitize the filename
        flat_name=$(sanitize_filename "$flat_name")
        
        # Copy file to target directory with new name
        cp "$file" "${target_dir}/${flat_name}"
        echo "Copied: ${file} -> ${target_dir}/${flat_name}" >> "${LOG_FILE}"
    done
    
    echo "Finished flattening repository $repo_name"
}

# Process each product's repositories
process_product_repos() {
    local product="$1"
    local repos_dir="$ROOT_DIR/tools/data-stores/$product/repos"
    local output_dir="$ROOT_DIR/tools/data-stores/$product/repo"
    
    echo "Processing $product repositories from $repos_dir to $output_dir"
    echo "Processing $product repositories" >> "${LOG_FILE}"
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Get list of repositories (directories only)
    for repo_dir in "$repos_dir"/*/ ; do
        if [ -d "$repo_dir" ]; then
            # Get repository name from directory path
            repo_name=$(basename "$repo_dir")
            
            echo "Processing repository: $repo_name"
            echo "Processing repository: $repo_name" >> "${LOG_FILE}"
            
            # Flatten the repository
            flatten_directory "$repo_dir" "$output_dir" "$repo_name"
            
            echo "Repository $repo_name flattened successfully" >> "${LOG_FILE}"
        fi
    done
    
    echo "Completed processing all $product repositories"
}

# Main process
echo "Starting repository flattening process..."

# Process repositories for each product
for product in "looker" "bigquery" "dbt" "looker-studio" "omni"; do
    echo "Processing $product repositories..."
    process_product_repos "$product"
done

echo "Process completed at $(date)" >> "${LOG_FILE}"
echo "Repository flattening complete. Check ${LOG_FILE} for details." 