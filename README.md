# Simple_Spark_DDOS_Detector
Spark Streaming Application to detect DDOS Attack

# Problem Statement:
The customer runs a website and periodically is attacked by a botnet in a Distributed Denial of Service (DDOS) attack. You’ll be given a log file in Apache log format from a given attack. Use this log to build a simple real-time detector of DDOS attacks.

# Requirements:
1. Ingest

  Read a file from local disk and write to a message system such as Kafka.

2. Detection

  Write an application which reads messages from the message system and detects whether the attacker is part of the DDOS attack

  Once an attacker is found, the ip-address should be written to a results directory which could be used for further processing

  An attack should be detected one to two minutes after starting
    
# Solution:

Assuming at a given second a botnet sends more than a threshold number of requests, all IP addresses sending more that threshold number of requests per second will be marked as suspicious botnet attack. Example - A machine 155.157.240.217 sends request at [25/May/2015:23:11:15 +0000] more than threshold number of times. This system will detect it as botnet attack.
