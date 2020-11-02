# Simple_Spark_DDOS_Detector
Spark Streaming Application to detect DDOS Attack

# Problem Statement:
The customer runs a website and periodically is attacked by a botnet in a Distributed Denial of Service (DDOS) attack. You’ll be given a log file in Apache log format from a given attack. Use this log to build a simple real-time detector of DDOS attacks.

# Requirements:
1.Ingest

  Read a file from local disk and write to a message system such as Kafka.

2.Detection

  Write an application which reads messages from the message system and detects whether the attacker is part of the DDOS attack

  Once an attacker is found, the ip-address should be written to a results directory which could be used for further processing

  An attack should be detected one to two minutes after starting
    
# Solution:

Assuming at a given instance of time a botnet sends more than a threshold number of requests, all IP addresses sending more that threshold number of requests at an instance will be marked as suspicious botnet attack. Example - A machine 155.157.240.217 sends request at [25/May/2015:23:11:15 +0000] more than threshold number of times. This system will detect it as botnet attack.


# Apache log message format

`200.4.91.190 - - [25/May/2015:23:11:15 +0000] "GET / HTTP/1.0" 200 3557 "-" "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)"`
For more information please read [apache log format](http://httpd.apache.org/docs/current/mod/mod_log_config.html)



# Technologies Used:

Spark 2.4.4

Kafka 2.6.0

Python 3.7


# Steps:

For Windows:

1. Start Zookeeper: `%KAFKA_HOME%\bin\windows\zookeeper-server-start.bat %KAFKA_HOME%\config\zookeeper.properties`

2. Start Kafka: `%KAFKA_HOME%\bin\windows\kafka-server-start.bat %KAFKA_HOME%\config\server.properties`

3. Start a Kafka Topic: `%KAFKA_HOME%\bin\windows\kafka-topics.bat --create --topic DDOS --bootstrap-server localhost:9092`

4. Start a Kafka Producer to ingest data to a topic: `%KAFKA_HOME%\bin\windows\kafka-console-producer.bat --broker-list localhost:9092 --topic DDOS < apache_logs.txt`
OR run `python src/main/python/python_kafka_producer.py` to read the file and ingest the contents to Kafka Topic

5. Run the command `spark2-submit --master local[*] --jars kafka-clients-0.10.1.0.jar,spark-sql-kafka-0-10_2.11-2.4.4.jar stream_kafka_consumer.py`


The Spark Application reads the data from the Kafka Topic and uses Regular Expression to get host, timestamp, status code etc information and identifies the host sending more than threshold number of requests at a given instance of time and marks it as botnet attack.
