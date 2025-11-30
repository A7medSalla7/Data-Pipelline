from kafka import KafkaConsumer
from pymongo import MongoClient
import json, time

def start_consumer():
    while True:
        try:
            consumer = KafkaConsumer(
                'Data-Sensor',
                bootstrap_servers='127.0.0.1:9094',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                consumer_timeout_ms=10000
            )

            mongo = MongoClient("mongodb://localhost:27017")
            collection = mongo.IOT_sensor.Data_sensor

            print("Consumer running...")

            for msg in consumer:
                collection.insert_one(msg.value)
                print("Inserted:", msg.value)

        except Exception as e:
            print("Error:", e)
            print("Reconnecting in 5 seconds...")
            time.sleep(5)

start_consumer()
