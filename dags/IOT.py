import json
import random
from datetime import datetime, timedelta
from airflow import DAG
# from airflow_provider_kafka.operators.produce_to_topic import ProduceToTopicOperator

KAFKA_BROKER = "old_kafka:9092"  # Kafka container name + port

# Default DAG args
default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 10, 24),
    "retries": 0,
}

# Callable function to generate and encode sensor data
def produce_sensor_data():
    temp = 27.5 + random.uniform(-0.2, 0.2)
    DO = 6 + random.uniform(-0.095, 0.1)
    PH = 7.5 + random.uniform(-0.1, 0.1)
    Ammonia = 0.01 + random.uniform(-0.0008, 0.0008)
    Nitrite = 0.05 + random.uniform(-0.004, 0.005)
    Turbidty = 40 + random.uniform(-1, 1)

    data = {
        "time": datetime.now().isoformat(),
        "temperature": temp,
        "Dissolved_oxygen": DO,
        "PH": PH,
        "Ammonia": Ammonia,
        "Nitrite": Nitrite,
        "Turbidty": Turbidty
    }

    # ProduceToTopicOperator expects bytes
    return json.dumps(data).encode("utf-8")


# DAG definition
with DAG(
    dag_id="iot_kafka_produce_only",
    default_args=default_args,
    description="Produce simulated IoT data to Kafka",
    schedule=timedelta(seconds=25),
    catchup=False,
    tags=["iot", "kafka"],
) as dag:

    send_to_kafka = ProduceToTopicOperator(
        task_id="send_to_kafka",
        topic="Data-Sensor",
        producer_function=produce_sensor_data,  # direct callable
        kafka_config={"bootstrap.servers": "kafka_old:9092"},
    )
