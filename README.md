 IoT Sensor Data Pipeline

This project is a complete **data pipeline** built using **Apache Airflow**, **Python**, and **MongoDB** to simulate and manage IoT sensor data.

 Overview
The pipeline automatically generates fake IoT sensor readings (like temperature, humidity, etc.), stores them in a MongoDB database, and can trigger notifications or further data processing.
 Components
- **Apache Airflow** – Task orchestration and scheduling  
- **Python** – Data generation and processing scripts  
- **MongoDB** – NoSQL database for sensor data storage  
- **Celery Executor** – Parallel task execution  
- **Docker** – Containerized environment  

DAG Tasks
1. **generate_sensor_data** → Simulates IoT data.  
2. **store_in_database** → Saves data to MongoDB.  
3. **notify_and_mail** → Sends email or log notifications on success/failure.  

 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/A7medSalla7/Data-Pipelline.git
