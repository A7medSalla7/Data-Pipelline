from datetime import datetime
import random
from pymongo import MongoClient
from confluent_kafka  import Producer , Consumer
import json

def generate_and_insert_sensor_data():
    """
    Simulate IoT sensor readings, insert into MongoDB,
    and send to Kafka in JSON format.
    """
    # --- MongoDB ---
    # client = MongoClient("mongodb://localhost:27017/")  # MongoDB container name
    # db = client["IOT_sensor"]
    # collection = db["Data_sensor"]

    # --- Kafka ---
    producer = Producer({'bootstrap.servers': 'kafka:9092'})  # Kafka container name

    # --- Sensor values ---
    temp, DO, PH = 27.5, 6, 7.5
    Ammonia, Nitrite, Turbidty = 0.01, 0.05, 40

    # --- Generate reading ---
    t = datetime.now()
    temp += random.uniform(-0.2, 0.2)
    DO += random.uniform(-0.095, 0.1)
    PH += random.uniform(-0.1, 0.1)

    old_Ammonia = Ammonia
    Ammonia += random.uniform(-0.0008, 0.0008)
    if Ammonia < 0: Ammonia = old_Ammonia

    old_Nitrite = Nitrite
    Nitrite += random.uniform(-0.004, 0.005)
    if Nitrite < 0: Nitrite = old_Nitrite

    Turbidty += random.uniform(-1, 1)

    # --- Prepare data dictionary ---
    data = {
        "time": t.isoformat(),
        "temperature": temp,
        "Dissolved_oxygen": DO,
        "PH": PH,
        "Ammonia": Ammonia,
        "Nitrite": Nitrite,
        "Turbidty": Turbidty
    }

    # # --- Insert into MongoDB ---
    # result = collection.insert_one(data)
# 
    # # --- Add MongoDB _id as string to data for Kafka ---
    # data["_id"] = str(result.inserted_id)

    # --- Send to Kafka ---
    producer.produce("Data-Sensor", json.dumps(data).encode("utf-8"))
    producer.flush()

    # # --- Close MongoDB connection ---
    # client.close()





def consume_and_store():
    # ---- KAFKA CONFIG ----
    consumer_conf = {
        'bootstrap.servers': 'localhost:9092',
       "group.id": "airflow-consumer",
        'auto.offset.reset': 'earliest'
    }

    topic = "Data-Sensor"

    consumer = Consumer(consumer_conf)
    consumer.subscribe([topic])

    # ---- MONGO CONFIG ----
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["IOT_sensor"]
    collection = db["Data_sensor"]

    messages = []
    print("Starting to poll...")

    # Consume max 100 messages per run
    for _ in range(100):
        msg = consumer.poll(1.0)
        if msg is None:
            break
        if msg.error():
            print("Error:", msg.error())
            continue

        try:
            value = json.loads(msg.value().decode("utf-8"))
        except:
            value = {"raw": msg.value().decode("utf-8")}

        messages.append(value)

    if messages:
        collection.insert_many(messages)
        print(f"Inserted {len(messages)} messages into MongoDB.")
    else:
        print("No messages consumed.")

    consumer.close()


# Run the function
generate_and_insert_sensor_data()


