# 🚲 Real-Time Velib Bike Availability Monitoring System

## 📌 Project Description

This project implements a **real-time big data streaming pipeline** to monitor **Velib bike availability** across stations.
It demonstrates the integration of **Apache Kafka**, **Apache Spark Structured Streaming**, **Hadoop**, **InfluxDB**, and **Grafana** to ingest, process, store, and visualize streaming data in real time.

The system continuously ingests Velib station status data, processes it using Spark, stores aggregated metrics in InfluxDB, and visualizes station occupancy trends using Grafana dashboards.

---

## 🏗️ Architecture Overview

**Technologies Used**

* Apache Kafka – Real-time data ingestion
* Apache Spark (Structured Streaming) – Stream processing
* Hadoop (HDFS + YARN) – Distributed storage & resource management
* InfluxDB – Time-series database
* Grafana – Real-time monitoring and visualization

---

## 🖥️ Cluster Setup

### Virtual Machines Configuration
----------------------------------------------- 
**VM1 (Master)**- Spark Master, Kafka Broker 0, InfluxDB, Grafana 
**VM2 (Worker)**- Spark Worker,Kafka , Broker 1                  

---

## 📂 Repository Structure

```
velib-bike-availability-monitoring/
│
├── config/
│   ├── core-site.xml
│   ├── hdfs-site.xml
│   ├── yarn-site.xml
│   ├── spark-defaults.conf
│   └── master-kafka-server.properties
│   └── worker-kafka-server.properties
|
│
├── producer/
│   └── produce_velib_data.py          # Kafka producer
│
├── spark/
│   └── velib_streaming.py              # Spark Structured│
├
|── sample-data/
│   └── velib_sample.json               # Sample test data
│
export
│
├── README.md
├── LICENSE
```

---

## ⚙️ Dependencies

### Software Versions

| Component | Version    |
| --------- | ---------- |
| Java      | OpenJDK    |
|           | 11.0.29    |
| Hadoop    | 3.3.6      |
| Spark     | 3.5.7      |
| Scala     | 2.12.18    |
| Kafka     | 3.6.0      |
| Python    | 3.12.3     |
| InfluxDB  | 2.7.1      |
| Grafana   | 10.2.0     |

---

## ▶️ How to Run the Project

### 1️⃣ Login to the Virtual Machines

**Master VM**

```bash
ssh adm-mcsc@esilv-mcscin5a1825-0076.westeurope.cloudapp.azure.com
```

**Worker VM**

```bash
ssh adm-mcsc@esilv-mcscin5a1825-0077.westeurope.cloudapp.azure.com
```

---

### 2️⃣ Start Hadoop Services (Master)

```bash
start-dfs.sh
start-yarn.sh
jps
```

---

### 3️⃣ Start Kafka Services

#### On Master VM

```bash
cd /opt/kafka/kafka_2.13-3.6.0
bin/zookeeper-server-start.sh -daemon config/zookeeper.properties
bin/kafka-server-start.sh -daemon config/server.properties
```

#### On Worker VM

```bash
cd /opt/kafka/kafka_2.13-3.6.0
bin/kafka-server-start.sh -daemon config/server.properties
```

Verify Kafka:

```bash
lsof -iTCP -sTCP:LISTEN -n -P | grep 9092
```

---

### 4️⃣ Create Kafka Topic

```bash
bin/kafka-topics.sh --create \
--topic velib-station-status \
--bootstrap-server 10.0.0.82:9092,10.0.0.83:9092 \
--replication-factor 2 \
--partitions 3
```

---

### 5️⃣ Activate Python Environment (Master)

```bash
source ~/pyspark-venv/bin/activate
```

---

### 6️⃣ Run Kafka Producer

```bash
cd ~/velibBikeAvailabilityprojects
python3 produce_velib_data.py
```

This continuously publishes Velib station data to Kafka.

---

### 7️⃣ Start InfluxDB

```bash
cd ~/influxdb2_linux_amd64
./influxd
```

Tunnel:

```bash
ssh -L 8086:10.0.0.82:8086 adm-mcsc@esilv-mcscin5a1825-0076.westeurope.cloudapp.azure.com
```

Access:

```
http://localhost:8086
```

---

### 8️⃣ Run Spark Streaming Job

```bash
spark-submit \
--master yarn \
--deploy-mode client \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.7 \
--py-files /home/adm-mcsc/pyspark-venv/lib/python3.12/site-packages/influxdb_client.zip,\
/home/adm-mcsc/pyspark-venv/lib/python3.12/site-packages/reactivex.zip \
spark/velib_streaming.py
```

---

## 📊 Monitoring & Visualization

### Grafana Setup

Start Grafana:

```bash
cd ~/grafana/grafana-10.2.0
./bin/grafana-server
```

Tunnel:

```bash
ssh -L 3000:10.0.0.82:3000 adm-mcsc@esilv-mcscin5a1825-0076.westeurope.cloudapp.azure.com
```

Access Grafana:

```
http://localhost:3000
```

Grafana is connected to **InfluxDB** to visualize:

* Total bikes available
* Dock availability
* Station occupancy percentage
* Real-time station status

---

## 📦 Sample Data

A small sample dataset is provided under:

```
04_sample-data/velib_sample.json
```

This can be used for testing without running the live producer.

---

## 🎥 Demo Video

📹 **Demo Video Link:**
👉 

---

## 📜 License

This project is licensed under the **MIT License**.
See the `LICENSE` file for details.

---

## ✅ Conclusion

This project demonstrates a complete **end-to-end real-time big data pipeline**, integrating multiple distributed systems and showcasing practical applications of streaming analytics and monitoring.

---

