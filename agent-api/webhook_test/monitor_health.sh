#!/bin/bash
# Script to monitor the health of the Vertex AI Agent webhook

# Set variables
PROJECT_ID=${PROJECT_ID:-"heuristicsai"}
REGION=${REGION:-"us-central1"}
FUNCTION_NAME=${FUNCTION_NAME:-"vertex-agent-tester"}

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo "Checking health of Vertex AI Agent webhook..."

# Check if the function exists
echo -e "${YELLOW}Checking if Cloud Function exists...${NC}"
FUNCTION_INFO=$(gcloud functions describe $FUNCTION_NAME --gen2 --region=$REGION --format="json" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Cloud Function '$FUNCTION_NAME' not found. Please deploy it first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Cloud Function exists${NC}"

# Get function URL
FUNCTION_URL=$(echo $FUNCTION_INFO | jq -r '.serviceConfig.uri')
echo "Function URL: $FUNCTION_URL"

# Check if function is active
echo -e "${YELLOW}Checking if Cloud Function is active...${NC}"
FUNCTION_STATE=$(echo $FUNCTION_INFO | jq -r '.state')

if [ "$FUNCTION_STATE" != "ACTIVE" ]; then
    echo -e "${RED}❌ Cloud Function is not active. Current state: $FUNCTION_STATE${NC}"
    echo "Check the function in the GCP Console: https://console.cloud.google.com/functions/details/$REGION/$FUNCTION_NAME?project=$PROJECT_ID"
    exit 1
fi

echo -e "${GREEN}✅ Cloud Function is active${NC}"

# Send a test request to the function
echo -e "${YELLOW}Sending test request to function...${NC}"
TEST_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/function_response.txt $FUNCTION_URL 2>/dev/null)
TEST_CONTENT=$(cat /tmp/function_response.txt)

if [ "$TEST_RESPONSE" != "200" ]; then
    echo -e "${RED}❌ Test request failed with status code: $TEST_RESPONSE${NC}"
    echo "Response body: $TEST_CONTENT"
    exit 1
fi

echo -e "${GREEN}✅ Function returned status code 200${NC}"

# Check Cloud Scheduler jobs
echo -e "${YELLOW}Checking Cloud Scheduler jobs...${NC}"
SCHEDULER_JOBS=$(gcloud scheduler jobs list --location=$REGION --format="json" | jq -c '.[] | select(.httpTarget.uri | contains("'$FUNCTION_NAME'"))' 2>/dev/null)

if [ -z "$SCHEDULER_JOBS" ]; then
    echo -e "${YELLOW}⚠️ No Cloud Scheduler jobs found for this function.${NC}"
    echo "Consider setting up a scheduler job for regular testing. Run the setup_scheduler.sh script."
else
    echo -e "${GREEN}✅ Found Cloud Scheduler jobs targeting this function:${NC}"
    echo $SCHEDULER_JOBS | jq -r '.name'
    
    # Check job statuses
    echo -e "${YELLOW}Checking job statuses...${NC}"
    for JOB in $(echo $SCHEDULER_JOBS | jq -r '.name'); do
        JOB_NAME=$(basename $JOB)
        JOB_STATE=$(gcloud scheduler jobs describe $JOB_NAME --location=$REGION --format="value(state)")
        
        if [ "$JOB_STATE" == "ENABLED" ]; then
            echo -e "${GREEN}✅ Job $JOB_NAME is enabled${NC}"
        else
            echo -e "${YELLOW}⚠️ Job $JOB_NAME is in state: $JOB_STATE${NC}"
        fi
    done
fi

# Check BigQuery table
echo -e "${YELLOW}Checking BigQuery dataset and table...${NC}"
DATASET=${BIGQUERY_DATASET:-"conversations"}
TABLE=${BIGQUERY_TABLE:-"bia"}

BQ_EXISTS=$(bq --format=json show $PROJECT_ID:$DATASET.$TABLE 2>/dev/null)

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️ BigQuery table $PROJECT_ID:$DATASET.$TABLE not found.${NC}"
    echo "The table will be created automatically when the function is first executed."
else
    echo -e "${GREEN}✅ BigQuery table exists${NC}"
    
    # Check recent records
    RECENT_COUNT=$(bq query --quiet --format=json --use_legacy_sql=false "SELECT COUNT(*) as count FROM \`$PROJECT_ID.$DATASET.$TABLE\` WHERE timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)" | jq -r '.[0].count')
    
    echo "Records in the last 24 hours: $RECENT_COUNT"
    
    if [ "$RECENT_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ Recent data is being logged to BigQuery${NC}"
    else
        echo -e "${YELLOW}⚠️ No recent data in BigQuery. The function may not have run recently or there might be issues with data logging.${NC}"
    fi
fi

echo -e "\n${GREEN}Health check complete!${NC}"
echo "For more detailed analysis, run the analyze_results.py script." 