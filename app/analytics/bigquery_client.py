# app/analytics/bigquery_client.py
"""
BigQuery client for analytics data collection.
"""

import os
import json
import tempfile
from datetime import datetime
from app.config import settings
from app.utils.logger import get_logger

# Attempt to import Google Cloud BigQuery
try:
    from google.cloud import bigquery
    BIGQUERY_AVAILABLE = True
except ImportError:
    bigquery = None
    BIGQUERY_AVAILABLE = False

logger = get_logger(__name__)

class BigQueryClient:
    def __init__(self):
        # Initialize BigQuery client
        # Make sure to set GOOGLE_APPLICATION_CREDENTIALS environment variable
        # or use service account credentials
        try:
            # Set credentials if provided
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
            
            self.client = bigquery.Client()
            self.project_id = settings.GOOGLE_CLOUD_PROJECT
            self.dataset_id = settings.BIGQUERY_DATASET_ID
            
            if not self.project_id:
                logger.warning("GOOGLE_CLOUD_PROJECT not set, BigQuery analytics will be disabled")
                self.client = None
            else:
                logger.info("BigQuery client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}")
            self.client = None
    
    def _check_dataset_exists(self):
        """Check if the dataset exists, create it if it doesn't."""
        if not self.client or not self.project_id:
            return False
            
        try:
            dataset_ref = self.client.dataset(self.dataset_id)
            self.client.get_dataset(dataset_ref)
            return True
        except Exception:
            # Dataset doesn't exist, try to create it
            try:
                dataset = bigquery.Dataset(f"{self.project_id}.{self.dataset_id}")
                dataset.location = "US"
                self.client.create_dataset(dataset, exists_ok=True)
                logger.info(f"Created BigQuery dataset: {self.dataset_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to create BigQuery dataset {self.dataset_id}: {e}")
                return False
    
    def _check_table_exists(self, table_name):
        """Check if a table exists, create it if it doesn't."""
        if not self.client or not self.project_id:
            return False
            
        try:
            table_ref = self.client.dataset(self.dataset_id).table(table_name)
            self.client.get_table(table_ref)
            return True
        except Exception:
            # Table doesn't exist, try to create it
            try:
                if table_name == "curriculum_generation":
                    schema = [
                        bigquery.SchemaField("timestamp", "TIMESTAMP"),
                        bigquery.SchemaField("curriculum_id", "STRING"),
                        bigquery.SchemaField("subject", "STRING"),
                        bigquery.SchemaField("path", "STRING"),
                        bigquery.SchemaField("module_count", "INTEGER"),
                        bigquery.SchemaField("success", "BOOLEAN"),
                        bigquery.SchemaField("fallback_used", "BOOLEAN"),
                        bigquery.SchemaField("recommended_tutor_style", "STRING"),
                    ]
                elif table_name == "api_usage":
                    schema = [
                        bigquery.SchemaField("timestamp", "TIMESTAMP"),
                        bigquery.SchemaField("model_name", "STRING"),
                        bigquery.SchemaField("success", "BOOLEAN"),
                        bigquery.SchemaField("error_message", "STRING"),
                        bigquery.SchemaField("quota_exceeded", "BOOLEAN"),
                    ]
                else:
                    return False
                
                table = bigquery.Table(f"{self.project_id}.{self.dataset_id}.{table_name}", schema=schema)
                self.client.create_table(table, exists_ok=True)
                logger.info(f"Created BigQuery table: {table_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to create BigQuery table {table_name}: {e}")
                return False
    
    def _batch_load_json_data(self, table_name, data):
        """
        Load data into BigQuery using batch loading.
        
        Args:
            table_name (str): The name of the table to load data into
            data (list): List of dictionaries containing the data to load
        """
        if not self.client or not self.project_id:
            logger.debug("BigQuery client not initialized, skipping batch load")
            return False
            
        try:
            # Create a temporary file with the data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                # Write data as JSON lines
                for record in data:
                    json.dump(record, temp_file)
                    temp_file.write('\n')
                temp_file_path = temp_file.name
            
            # Configure the load job
            dataset_ref = self.client.dataset(self.dataset_id)
            table_ref = dataset_ref.table(table_name)
            
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                autodetect=False,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            )
            
            # Load the data
            with open(temp_file_path, "rb") as source_file:
                load_job = self.client.load_table_from_file(
                    source_file, table_ref, job_config=job_config
                )
            
            # Wait for the job to complete
            load_job.result()
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            logger.info(f"Successfully batch loaded {len(data)} records to {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error batch loading data to BigQuery: {e}")
            # Clean up the temporary file if it exists
            try:
                os.unlink(temp_file_path)
            except:
                pass
            return False
    
    def log_curriculum_generation(self, curriculum_data, success=True, fallback_used=False):
        """
        Log curriculum generation event to BigQuery.
        Tries batch loading first, falls back to logging to file if permissions are insufficient.
        
        Args:
            curriculum_data (dict): The curriculum data generated
            success (bool): Whether the generation was successful
            fallback_used (bool): Whether fallback to mock data was used
        """
        if not self.client or not self.project_id:
            logger.debug("BigQuery client not initialized or project ID not set, skipping curriculum generation log")
            return
        
        try:
            # Check if dataset and table exist, create if needed
            if not self._check_dataset_exists():
                logger.warning("BigQuery dataset not available, skipping log")
                return
                
            if not self._check_table_exists("curriculum_generation"):
                logger.warning("BigQuery curriculum_generation table not available, skipping log")
                return
            
            # Prepare the data for insertion
            row = {
                "timestamp": datetime.utcnow().isoformat(),
                "curriculum_id": curriculum_data.get("curriculum_id", ""),
                "subject": curriculum_data.get("subject_id", ""),
                "path": curriculum_data.get("path", ""),
                "module_count": len(curriculum_data.get("modules", [])),
                "success": success,
                "fallback_used": fallback_used,
                "recommended_tutor_style": curriculum_data.get("recommended_tutor_style", ""),
            }
            
            # Try batch loading the data
            success = self._batch_load_json_data("curriculum_generation", [row])
            
            if success:
                logger.info("Successfully logged curriculum generation to BigQuery")
            else:
                # Fallback to file logging if BigQuery fails
                self._log_to_file("curriculum_generation", [row])
                
        except Exception as e:
            logger.error(f"Error logging to BigQuery: {e}")
            # Fallback to file logging if BigQuery fails
            try:
                row = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "curriculum_id": curriculum_data.get("curriculum_id", ""),
                    "subject": curriculum_data.get("subject_id", ""),
                    "path": curriculum_data.get("path", ""),
                    "module_count": len(curriculum_data.get("modules", [])),
                    "success": success,
                    "fallback_used": fallback_used,
                    "recommended_tutor_style": curriculum_data.get("recommended_tutor_style", ""),
                }
                self._log_to_file("curriculum_generation", [row])
            except Exception as e2:
                logger.error(f"Error logging to file: {e2}")
    
    def log_api_usage(self, model_name, success=True, error_message=None, quota_exceeded=False):
        """
        Log API usage statistics to BigQuery.
        Tries batch loading first, falls back to logging to file if permissions are insufficient.
        
        Args:
            model_name (str): The name of the model used
            success (bool): Whether the API call was successful
            error_message (str): Error message if failed
            quota_exceeded (bool): Whether the failure was due to quota limits
        """
        if not self.client or not self.project_id:
            logger.debug("BigQuery client not initialized or project ID not set, skipping API usage log")
            return
        
        try:
            # Check if dataset and table exist, create if needed
            if not self._check_dataset_exists():
                logger.warning("BigQuery dataset not available, skipping log")
                return
                
            if not self._check_table_exists("api_usage"):
                logger.warning("BigQuery api_usage table not available, skipping log")
                return
            
            # Prepare the data for insertion
            row = {
                "timestamp": datetime.utcnow().isoformat(),
                "model_name": model_name,
                "success": success,
                "error_message": error_message or "",
                "quota_exceeded": quota_exceeded,
            }
            
            # Try batch loading the data
            success = self._batch_load_json_data("api_usage", [row])
            
            if success:
                logger.info("Successfully logged API usage to BigQuery")
            else:
                # Fallback to file logging if BigQuery fails
                self._log_to_file("api_usage", [row])
                
        except Exception as e:
            logger.error(f"Error logging to BigQuery: {e}")
            # Fallback to file logging if BigQuery fails
            try:
                row = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "model_name": model_name,
                    "success": success,
                    "error_message": error_message or "",
                    "quota_exceeded": quota_exceeded,
                }
                self._log_to_file("api_usage", [row])
            except Exception as e2:
                logger.error(f"Error logging to file: {e2}")
    
    def _log_to_file(self, log_type, data):
        """
        Fallback method to log data to a local file when BigQuery is not available.
        
        Args:
            log_type (str): Type of log (curriculum_generation or api_usage)
            data (list): List of dictionaries containing the data to log
        """
        try:
            # Create logs directory if it doesn't exist
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Write to log file
            log_file = os.path.join(log_dir, f"{log_type}.log")
            with open(log_file, "a") as f:
                for record in data:
                    f.write(f"{json.dumps(record)}\n")
            
            logger.info(f"Logged {len(data)} records to {log_file} (BigQuery unavailable)")
        except Exception as e:
            logger.error(f"Error logging to file: {e}")

# Global instance
bigquery_client = BigQueryClient()