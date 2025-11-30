from datetime import datetime, timedelta
import random
# from pymongo import MongoClient
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
# from plyer import notification
import smtplib
from email.mime.text import MIMEText
from confluent_kafka  import Producer , Consumer
import json






def generate_and_insert_sensor_data():
    """
    Simulate IoT sensor readings, insert them into MongoDB,
    and send the data to Kafka in JSON format.
    """
    # Connect to MongoDB
    # client = MongoClient("mongodb://host.docker.internal:27017/")
    # db = client["IOT_sensor"]
    # collection = db["Data_sensor"]

    # Connect to Kafka
    p = Producer({'bootstrap.servers': 'kafka:9092'})


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

    # Prepare data dictionary
    data = {
        "time": t.isoformat(),  # convert datetime to string
        "temperature": temp,
        "Dissolved_oxygen": DO,
        "PH": PH,
        "Ammonia": Ammonia,
        "Nitrite": Nitrite,
        "Turbidty": Turbidty
    }

    # Insert into MongoDB
    # result = collection.insert_one(data)

    # # Add MongoDB _id as string to the data for Kafka
    # data["_id"] = str(result.inserted_id)

    # print(f"[{t}] Inserted sensor data:", data)

    # Close MongoDB client
    # client.close()

    # Send to Kafka
    def delivery_report(err, msg):
        if err:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    p.produce("Data-Sensor", json.dumps(data).encode('utf-8'), callback=delivery_report)
    p.flush()





def notify_and_mail():
   
    # notification.notify(
    #     title="ERROR",
    #     message="Sensors aren't sending data. There is an error.",
    #     app_name="Sensors",
    #     timeout=5  
    # )

    sender = receiver = "ahmed.cse.zu@gmail.com"


    msg = MIMEText("Sensors aren't sending data. Please check the system.")

    msg["Subject"] = "Sensor Error Alert"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, "fhpk jmty urzw vxcs")
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)




# def consume_and_store():
#     # ---- KAFKA CONFIG ----
#     consumer_conf = {
#         'bootstrap.servers': 'kafka:9092',
#         'group.id': 'console-consumer-37599',
#         'auto.offset.reset': 'earliest'
#     }

#     topic = "Data-Sensor"

#     consumer = Consumer(consumer_conf)
#     consumer.subscribe([topic])

#     # ---- MONGO CONFIG ----
#     mongo_client = MongoClient("mongodb://host.docker.internal:27017/")
#     db = mongo_client["IOT_sensor"]
#     collection = db["Data_sensor"]

#     messages = []
#     print("Starting to poll...")

#     # Consume max 100 messages per run
#     for _ in range(100):
#         msg = consumer.poll(1.0)
#         if msg is None:
#             break
#         if msg.error():
#             print("Error:", msg.error())
#             continue

#         try:
#             value = json.loads(msg.value().decode("utf-8"))
#         except:
#             value = {"raw": msg.value().decode("utf-8")}

#         messages.append(value)

#     if messages:
#         collection.insert_many(messages)
#         print(f"Inserted {len(messages)} messages into MongoDB.")
#     else:
#         print("No messages consumed.")

#     consumer.close()

    



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
    schedule=timedelta(seconds=25), 
    catchup=False,
    tags=["iot", "mongodb"],
) as dag:

    generate_data_task = PythonOperator(
        task_id="generate_sensor_data",
        python_callable=generate_and_insert_sensor_data,
    )
       
    # consume_task = PythonOperator(
    #     task_id="consume_kafka",
    #     python_callable=consume_and_store,

    # )

    notify_me = PythonOperator(
        task_id="notify_and_mail_if_fail",
        python_callable=notify_and_mail,
        trigger_rule="one_failed"
    )


    generate_data_task >> notify_me # >>  consume_task # 
