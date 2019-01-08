### ETL-Big-Data-Pipeline
## Overview
ETL Big Data Pipeline for log files using the Hortonworks HDP distribution. Built using Nifi interface with Kafka, Flume, Oozie, Spark Streaming, Cassandra and HDFS.
This pipeline starts at a log file containing records of Errors and Warnings ocuring on a web server. Everytime new records are appended to this file, they are sent down the pipeline one line at a time. 
Lines are routed to a Kafka topic depending on if they contain certain keywords, and then sinked into HDFS using flume.
An Oozie coordinator job is used to apply a Spark Streaming job with a 1 minute time window and a slider interval of 5 secs. This Spark Streaming job counts the number of lines containing each keyword and then streams results to a Kafka topic.
From this Kafka topic, final results are sinked as records into a Cassandra database and also sinked sequentially into HDFS.

##Tools Used
**Nifi:** An software tool that allows users to build complex data flow pipelines quickly. It handles data flow from external data sources into the Hadoop cluster.
**Kafka:** A distributed streaming platform that is used to reliably publish and subscribe to streams of recrods
**Flume:** A software service for efficiently colelcting, aggregating and moving large amounts of streaming log files
**Oozie:** A workflow scheduler system to manage Hadoop jobs
**Spark Streaming:** An open source general-purpose distributed computing enginge used for processing and analyzing streaming big data sets in micro-batches
**Cassandra:** A distributed, wide column store NoSQL database designed for handling big data
**HDFS:** The primary data storage system used by Hadoop that is high-performing and highly scalable

##Architecture
The architecture of the pipeline is as shown below. 
![Alt text](images/architecture.PNG?raw=true "Architecture")

##Nifi UI Pipeline
The completed Nifi pipeline is shown below
![Alt text](images/Nifi_pipeline.png?raw=true "Nifi Pipeline")'

##Files Included
**Nifi/**
	**ETL_Pipeline_Nifi.xml**: An importable Nifi template for the pipeline shown above
	**Description.docx** : A description of all Nifi components used and their configurations
**Final-Sinks** : A dump of the contents of the final Cassandra and HDFS sinks after a cycle throguh the pipeline
**Input/**
	**error_log.txt** : The data set used for development
	**streaming_results_to_test_cassandra** : Dataset taken from subset of spark streaming job output that was used to test the cassandra consumer in Nifi
**Oozie/**
	**coordinator.xml** : The Oozie job coordinator configuration file
	**job.properties** : The Oozie job properties configuration file
	**workflow.xml** : The Oozie workflow configuration file

##Instructions
1.	Install Hortonworks HDP with Nifi

2. 	Open Nifi UI and import the "ETL_Pipeline_Nifi.xml" Nifi template file

3.	Store files on Hadoop as indicated in the "Nifi/Description.docx" file

4.	Create Kafka Topics: 
	/usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create --zookeeper sandbox.hortonworks.com:2181 --replication-factor	1  --partition 1 --topic CISC432
	
5.	Run Kafka Producer:
	/usr/hdp/current/kafka-broker/bin/kafka-console-producer.sh --broker-list sandbox-hdrtonworks.com:6667 --topic Error 
	
6.	Run Kafka Consumer:
	/usr/hdp/current/kafka-broker/bin/kafka-console-consumer.sh --zookeeper localhost:2181 --topic Error
	
7.	Install Cassandra:
	#ssh -p 2222 root@localhost
	#swtich to 2.7 using scl
	#scl software collection command to switch between python versions. 
	scl enable python27 bash
	#You should see Python 2.7 (You always have to do this before running Cassandra)
	python -V
	service cassandra start 
	#wait like 3-5 minutes
	#cqlsh "will ask your for a version"
	cqlsh --cqlversion="3.4.4"

8.	Create Cassandra Keyspace
	create keyspace a3space WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 } ; 
	
9.	Create Cassandra Table
	CREATE TABLE IF NOT exists a3space.results (LogType varchar, Timestamp timestamp, Count int, PRIMARY KEY ((LogType), Timestamp));

7. Run Oozie job
	oozie job -oozie http://localhost:11000/oozie -config /home/maria_dev/job.properties -run