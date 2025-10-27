from airflow import DAG
from airflow.operators.bash import BashOperator  
from datetime import datetime

with DAG(
    dag_id="my_first_dag",
    description="simple",         
    start_date=datetime(2025, 9, 7),
    catchup=False,
    tags=["DEPI"]                 
) as dag:
    task1 = BashOperator(
        task_id="print",
        bash_command="echo 'HELLO ya AHMED'"   
    )

    task1