#!/bin/bash
# Deployment script for Vertex AI Agent Test Webhook

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed. Please install it first."
    exit 1
fi

echo "Deploying Vertex AI Agent Test Webhook to Cloud Functions..."

# Set variables
PROJECT_ID=${PROJECT_ID:-"heuristicsai"}
REGION=${REGION:-"us-central1"}
FUNCTION_NAME=${FUNCTION_NAME:-"vertex-agent-tester"}
VERTEX_AI_APP_ID=${VERTEX_AI_APP_ID:-"8285e0d0-24ae-43e9-8491-b0bd99befc87"}
BIGQUERY_DATASET=${BIGQUERY_DATASET:-"conversations"}
BIGQUERY_TABLE=${BIGQUERY_TABLE:-"bia"}
LOCATION=${LOCATION:-"global"}

# Deploy the function
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=test_vertex_agent \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,LOCATION=$LOCATION,VERTEX_AI_APP_ID=$VERTEX_AI_APP_ID,BIGQUERY_DATASET=$BIGQUERY_DATASET,BIGQUERY_TABLE=$BIGQUERY_TABLE

if [ $? -eq 0 ]; then
    echo "✅ Function deployed successfully!"
    
    # Get the function URL
    FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --gen2 --region=$REGION --format="value(serviceConfig.uri)")
    
    echo "Your function is available at: $FUNCTION_URL"
    echo ""
    echo "To test the function with the predefined questions, run:"
    echo "curl $FUNCTION_URL"
    echo ""
    echo "To test with custom questions, run:"
    echo "curl -X POST $FUNCTION_URL \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"questions\": [\"Your test question here?\"]}'"
    echo ""
    echo "To set up scheduled testing, go to:"
    echo "https://console.cloud.google.com/cloudscheduler"
else
    echo "❌ Function deployment failed. Check the error messages above."
fi 