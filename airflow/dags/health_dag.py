"""
File for simple health check DAG.
This DAG will run periodically to check the health of the application by making a request to the health endpoint. It can be used to monitor the application's health and alert if it becomes unresponsive.
"""

# Import external libraries
from datetime import datetime, timedelta

import psycopg2
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator


def hello_world():
    """
    Simple hello world function to test if the DAG is working.
    """
    print("Hello from Airflow!")
    return "success"


def check_services():
    """
    Check if other services are accessible.
    This can include making requests to the API health endpoint, checking database connectivity, etc.
    """

    try:
        # Check API health
        response = requests.get(
            "http://paperlens-api:8585/api/v1/health",
            timeout=5,
        )
        print(f"API Health: {response.status_code}")

        # Check database connection
        connection = psycopg2.connect(
            host="postgres",
            port=5432,
            database="paperlens_db",
            user="paperlens_user",
            password="paperlens_password",
        )
        print("Database: Connected successfully")
        connection.close()

        return "Services are healthy and accessible"

    except Exception as e:
        print(f"Service check failed: {e}")
        raise


# DAG Configuration
airflow_dag_config = {
    "owner": "paperlens",
    "depends_on_past": False,
    "start_date": datetime(2026, 4, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


# Create the DAGs and tasks
dag = DAG(
    "hello_world_dag",
    default_args=airflow_dag_config,
    description="A simple DAG to test Airflow setup and check service health.",
    schedule=None,  # Set to None for manual trigger, or use a cron expression for periodic runs
    catchup=False,
    tags=["health", "testing"],
)

# Define the tasks
hello_world_task = PythonOperator(
    task_id="hello_world_task",
    python_callable=hello_world,
    dag=dag,
)

service_check_task = PythonOperator(
    task_id="check_services_task",
    python_callable=check_services,
    dag=dag,
)

# Set task dependencies
hello_world_task >> service_check_task
