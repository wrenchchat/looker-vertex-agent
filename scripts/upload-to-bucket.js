const fs = require('fs');
const path = require('path');
const { Storage } = require('@google-cloud/storage');
const storage = new Storage();

// Configuration
const SOURCE_ROOT = path.join(__dirname, 'data-stores');

// Use the correct buckets specified in Vertex_AI_Agent_Plan.md
const PRODUCT_BUCKETS = {
  'bigquery': 'bia-bigquery',
  'dbt': 'bia-dbt',
  'looker': 'bia-looker',
  'looker-studio': 'bia-looker-studio',
  'omni': 'bia-omni'
};

async function uploadDirectory(localDirPath, bucketName, destDirPath) {
  if (!fs.existsSync(localDirPath)) {
    console.log(`Directory does not exist: ${localDirPath}`);
    return;
  }

  console.log(`Uploading from ${localDirPath} to ${bucketName}/${destDirPath}`);
  
  try {
    // Check if bucket exists - but don't create it if it doesn't
    const bucket = storage.bucket(bucketName);
    const [exists] = await bucket.exists();
    
    if (!exists) {
      console.error(`Error: Bucket "${bucketName}" does not exist. Please create it first.`);
      return;
    }
    
    // Get all files in the directory
    const files = fs.readdirSync(localDirPath);
    
    for (const file of files) {
      const localFilePath = path.join(localDirPath, file);
      const stats = fs.statSync(localFilePath);
      
      if (stats.isDirectory()) {
        // Recursively upload subdirectories
        await uploadDirectory(
          localFilePath, 
          bucketName, 
          path.join(destDirPath, file)
        );
      } else {
        // Upload the file
        const destPath = path.join(destDirPath, file);
        await bucket.upload(localFilePath, {
          destination: destPath
        });
        console.log(`Uploaded: ${localFilePath} → ${bucketName}/${destPath}`);
      }
    }
    console.log(`Completed upload from ${localDirPath} to ${bucketName}/${destDirPath}`);
  } catch (error) {
    console.error(`Error uploading directory ${localDirPath}:`, error);
  }
}

async function uploadProduct(productName) {
  console.log(`\n======= Processing ${productName} =======`);
  const productDir = path.join(SOURCE_ROOT, productName);
  
  // Get the pre-defined bucket for this product
  const bucketName = PRODUCT_BUCKETS[productName];
  if (!bucketName) {
    console.error(`Error: No bucket defined for product "${productName}"`);
    return;
  }
  
  // Define source directories to upload
  const dirsToUpload = ['apis', 'docs', 'pdfs', 'repo'];
  
  for (const dir of dirsToUpload) {
    const localDirPath = path.join(productDir, dir);
    if (fs.existsSync(localDirPath)) {
      await uploadDirectory(localDirPath, bucketName, dir);
    } else {
      console.log(`Directory does not exist: ${localDirPath} - skipping`);
    }
  }
}

async function main() {
  try {
    console.log('Starting upload process...');
    
    // Process each product
    const products = Object.keys(PRODUCT_BUCKETS);
    for (const product of products) {
      await uploadProduct(product);
    }
    
    console.log('\nUpload process completed successfully!');
  } catch (error) {
    console.error('Error in main process:', error);
  }
}

// Run the main function
main(); 