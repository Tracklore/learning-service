# BigQuery Analytics Setup

This document explains how to set up and use BigQuery analytics for the learning service.

## Prerequisites

1. A Google Cloud Project with BigQuery API enabled
2. A service account with BigQuery permissions
3. The `google-cloud-bigquery` package installed

## Setup

1. **Enable BigQuery API**:
   - Go to the Google Cloud Console
   - Navigate to APIs & Services > Library
   - Search for "BigQuery API" and enable it

2. **Create a Dataset**:
   - In the BigQuery console, create a dataset named `learning_analytics` (or customize the name)
   - Set appropriate permissions for your service account

3. **Create Tables**:
   Create the following tables in your dataset:

   **curriculum_generation table**:
   ```sql
   CREATE TABLE `your-project.learning_analytics.curriculum_generation` (
     timestamp TIMESTAMP,
     curriculum_id STRING,
     subject STRING,
     path STRING,
     module_count INTEGER,
     success BOOLEAN,
     fallback_used BOOLEAN,
     recommended_tutor_style STRING
   )
   ```

   **api_usage table**:
   ```sql
   CREATE TABLE `your-project.learning_analytics.api_usage` (
     timestamp TIMESTAMP,
     model_name STRING,
     success BOOLEAN,
     error_message STRING,
     quota_exceeded BOOLEAN
   )
   ```

4. **Authentication**:
   Set up authentication using one of these methods:
   - Service account key file with `GOOGLE_APPLICATION_CREDENTIALS` environment variable
   - Workload Identity Federation (recommended for production)
   - Application Default Credentials

5. **Environment Variables**:
   Set the following environment variables:
   ```bash
   GOOGLE_CLOUD_PROJECT=your-project-id
   BIGQUERY_DATASET_ID=learning_analytics  # Optional, defaults to learning_analytics
   ```

## Data Collection

The system automatically collects the following data:

1. **Curriculum Generation Events**:
   - When a curriculum is successfully generated
   - When fallback to mock data is used
   - Curriculum metadata (subject, path, module count, etc.)

2. **API Usage Statistics**:
   - Model usage (which models are being used)
   - Success/failure rates
   - Error types and quota exceeded events

## Querying Data

You can query the collected data using standard SQL. Examples:

```sql
-- Get curriculum generation success rate
SELECT 
  COUNT(*) as total_requests,
  SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_requests,
  SUM(CASE WHEN fallback_used THEN 1 ELSE 0 END) as fallback_requests,
  AVG(CASE WHEN success THEN 1 ELSE 0 END) * 100 as success_rate
FROM `your-project.learning_analytics.curriculum_generation`

-- Get most popular subjects
SELECT 
  subject,
  COUNT(*) as generation_count
FROM `your-project.learning_analytics.curriculum_generation`
WHERE success = TRUE
GROUP BY subject
ORDER BY generation_count DESC

-- Get API usage by model
SELECT 
  model_name,
  COUNT(*) as request_count,
  SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_requests,
  SUM(CASE WHEN quota_exceeded THEN 1 ELSE 0 END) as quota_exceeded_count
FROM `your-project.learning_analytics.api_usage`
GROUP BY model_name
```

## Privacy and Compliance

Make sure to follow privacy best practices:
- Only collect necessary data
- Anonymize user identifiers when possible
- Follow your organization's data retention policies
- Ensure compliance with applicable regulations (GDPR, CCPA, etc.)