#!/bin/bash
# Script to set up Cloud Scheduler for regular testing of the Vertex AI Agent

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Set variables
PROJECT_ID=${PROJECT_ID:-"heuristicsai"}
REGION=${REGION:-"us-central1"}
FUNCTION_NAME=${FUNCTION_NAME:-"vertex-agent-tester"}
SCHEDULER_JOB_NAME=${SCHEDULER_JOB_NAME:-"vertex-agent-daily-test"}
SCHEDULE=${SCHEDULE:-"0 9 * * *"}  # Default: every day at 9 AM
TIMEZONE=${TIMEZONE:-"America/Los_Angeles"}

# Get the function URL
FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --gen2 --region=$REGION --format="value(serviceConfig.uri)")

if [ -z "$FUNCTION_URL" ]; then
    echo "❌ Error: Could not find the Cloud Function URL. Make sure the function is deployed."
    echo "Run the deploy.sh script first to deploy the function."
    exit 1
fi

echo "Setting up Cloud Scheduler job to test the Vertex AI Agent..."
echo "Function URL: $FUNCTION_URL"
echo "Schedule: $SCHEDULE ($TIMEZONE)"

# Create the scheduler job
gcloud scheduler jobs create http $SCHEDULER_JOB_NAME \
  --schedule="$SCHEDULE" \
  --uri="$FUNCTION_URL" \
  --http-method=GET \
  --time-zone="$TIMEZONE" \
  --location=$REGION \
  --project=$PROJECT_ID

if [ $? -eq 0 ]; then
    echo "✅ Cloud Scheduler job created successfully!"
    echo ""
    echo "Job '$SCHEDULER_JOB_NAME' will run on schedule: $SCHEDULE ($TIMEZONE)"
    echo ""
    echo "To view the job in the GCP Console, go to:"
    echo "https://console.cloud.google.com/cloudscheduler?project=$PROJECT_ID"
    echo ""
    echo "To test the job immediately, run:"
    echo "gcloud scheduler jobs run $SCHEDULER_JOB_NAME --location=$REGION"
else
    echo "❌ Cloud Scheduler job creation failed. Check the error messages above."
fi 