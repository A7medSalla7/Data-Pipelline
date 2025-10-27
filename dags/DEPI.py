from datetime import datetime, timedelta
import random
from pymongo import MongoClient
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from plyer import notification
import smtplib
from email.mime.text import MIMEText




def generate_and_insert_sensor_data():
    """
    Simulate IoT sensor readings and insert them into MongoDB.
    """
    client = MongoClient("mongodb://host.docker.internal:27017/")

    db = client["IOT_sensor"]
    collection = db["Data_sensor"]

    # Initialize static variables
    temp = 27.5
    DO = 6
    PH = 7.5
    Ammonia = 0.01
    Nitrite = 0.05
    Turbidty = 40

    # Generate one reading
    t = datetime.now()
    temp += random.uniform(-0.2, 0.2)
    DO += random.uniform(-0.095, 0.1)
    PH += random.uniform(-0.1, 0.1)

    old_Ammonia = Ammonia
    Ammonia += random.uniform(-0.0008, 0.0008)
    if Ammonia < 0:
        Ammonia = old_Ammonia

    old_Nitrite = Nitrite
    Nitrite += random.uniform(-0.004, 0.005)
    if Nitrite < 0:
        Nitrite = old_Nitrite

    Turbidty += random.uniform(-1, 1)

    data = {
        "time": t,
        "temperature": temp,
        "Dissolved_oxygen": DO,
        "PH": PH,
        "Ammonia": Ammonia,
        "Nitrite": Nitrite,
        "Turbidty": Turbidty
    }

    collection.insert_one(data)
    print(f"[{t}] Inserted sensor data:", data)
    client.close()


def notify_and_mail():
   
    notification.notify(
        title="ERROR",
        message="Sensors aren't sending data. There is an error.",
        app_name="Sensors",
        timeout=5  
    )

    sender = receiver = "ahmed.cse.zu@gmail.com"
    password="af098765"

    msg = MIMEText("Sensors aren't sending data. Please check the system.")
    msg = MIMEText("Sensors aren't sending data. Please check the system.")
    msg["Subject"] = "Sensor Error Alert"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)


# Default DAG arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 10, 24),
    "retries": 0,
    "retry_delay": timedelta(seconds=10),
}


with DAG(
    dag_id="iot_sensor_data_dag",
    default_args=default_args,
    description="Simulate IoT sensor readings and insert into MongoDB",
    schedule=timedelta(seconds=15), 
    catchup=False,
    tags=["iot", "mongodb"],
) as dag:

    generate_data_task = PythonOperator(
        task_id="generate_sensor_data",
        python_callable=generate_and_insert_sensor_data,
    )

    notify_me = PythonOperator(
        task_id="notify_and_mail_if_fail",
        python_callable=notify_and_mail,
        trigger_rule="one_failed"
    )

    generate_data_task >> notify_me
