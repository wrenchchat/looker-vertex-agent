# clone and flatten repos

#!/bin/bash

# Configuration
INPUT_MD_FILE="repos.md"    # Your markdown file containing repository URLs
OUTPUT_DIR="flattened_repos"  # Directory where all files will be stored
TEMP_DIR="temp_repos"         # Temporary directory for cloning
LOG_FILE="flatten_repos.log"  # Log file for operations

# Create necessary directories
mkdir -p "${OUTPUT_DIR}"
mkdir -p "${TEMP_DIR}"

# Initialize log file
echo "Repository flattening process started at $(date)" > "${LOG_FILE}"

# Function to extract GitHub URLs from markdown file
extract_urls() {
    # Look for URLs in the format https://github.com/...
    grep -o 'https://github.com/[^)"]*' "$1" | sort | uniq
}

# Function to sanitize filename
sanitize_filename() {
    echo "$1" | sed 's/[^a-zA-Z0-9._-]/_/g'
}

# Function to flatten a directory
flatten_directory() {
    local source_dir="$1"
    local target_dir="$2"
    local repo_name="$3"
    
    # Find all files (excluding .git directory)
    find "${source_dir}" -type f -not -path '*/\.*' | while read -r file; do
        # Get the original filename
        filename=$(basename "$file")
        
        # Create a unique name using repository name and original filename
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
}

# Main process
echo "Starting repository processing..."

# Extract URLs and process each repository
extract_urls "${INPUT_MD_FILE}" | while read -r repo_url; do
    echo "Processing repository: ${repo_url}"
    echo "Processing repository: ${repo_url}" >> "${LOG_FILE}"
    
    # Extract repository name from URL
    repo_name=$(echo "${repo_url}" | awk -F'/' '{print $(NF-1)"_"$NF}')
    repo_name=$(sanitize_filename "${repo_name}")
    
    # Create temporary directory for this repository
    temp_repo_dir="${TEMP_DIR}/${repo_name}"
    mkdir -p "${temp_repo_dir}"
    
    # Clone repository
    if git clone "${repo_url}" "${temp_repo_dir}"; then
        echo "Successfully cloned ${repo_url}" >> "${LOG_FILE}"
        
        # Flatten the repository
        flatten_directory "${temp_repo_dir}" "${OUTPUT_DIR}" "${repo_name}"
        
        # Clean up temporary repository
        rm -rf "${temp_repo_dir}"
        echo "Cleaned up temporary files for ${repo_name}" >> "${LOG_FILE}"
    else
        echo "Failed to clone ${repo_url}" >> "${LOG_FILE}"
    fi
done

# Clean up temporary directory
rm -rf "${TEMP_DIR}"

echo "Process completed at $(date)" >> "${LOG_FILE}"
echo "Repository flattening complete. Check ${LOG_FILE} for details."
