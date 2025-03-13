const fs = require('fs');
const path = require('path');
const { Storage } = require('@google-cloud/storage');

// Path to your service account key file
const keyFilePath = process.env.GOOGLE_APPLICATION_CREDENTIALS || 
                    path.join(process.env.HOME, '.config', 'gcloud', 'application_default_credentials.json');

// Check if the key file exists
if (!fs.existsSync(keyFilePath)) {
  console.error(`Error: Service account key file not found at ${keyFilePath}`);
  console.error('Please set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the path of your service account key file.');
  process.exit(1);
}

console.log(`Using service account key file: ${keyFilePath}`);

// Initialize storage with explicit credentials
const storage = new Storage({
  keyFilename: keyFilePath
});

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
    
    // List the buckets to verify credentials
    console.log('Verifying GCP credentials by listing buckets...');
    const [buckets] = await storage.getBuckets();
    console.log('Successfully authenticated with GCP. Found buckets:');
    buckets.forEach(bucket => {
      console.log(`- ${bucket.name}`);
    });
    
    console.log('\nProceeding with upload...');
    
    // Process each product
    const products = Object.keys(PRODUCT_BUCKETS);
    for (const product of products) {
      await uploadProduct(product);
    }
    
    console.log('\nUpload process completed successfully!');
  } catch (error) {
    console.error('Error in main process:', error);
    if (error.message && error.message.includes('authentication')) {
      console.error('\nAuthentication error. Make sure your service account key file is valid and has the correct permissions.');
      console.error('You can set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the path of your service account key file:');
      console.error('export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/keyfile.json');
    }
  }
}

// Run the main function
main(); 