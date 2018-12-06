# ETL-Big-Data-Pipeline
ETL Big Data Pipeline for log files using the Hortonworks HDP distribution. Built using Nifi interface with Kafka, Flume, Oozie, Spark Streaming, Cassandra and HDFS.
This pipeline starts at a log file containing records of Errors and Warnings ocuring on a web server. Everytime new records are appended to this file, they are sent down the pipeline one line at a time. 
Lines are routed to a Kafka topic depending on if they contain certain keywords, and then sinked into HDFS using flume.
An Oozie coordinator job is used to apply a Spark Streaming job with a 1 minute time window and a slider interval of 5 secs. This Spark Streaming job counts the number of lines containing each keyword and then streams results to a Kafka topic.
From this Kafka topic, final results are sinked as records into a Cassandra database and also sinked sequentially into HDFS.

The architecture of the pipeline is as shown below
![Alt text](images/architecture.png?raw=true "Architecture")

The completed Nifi pipeline is shown below
![Alt text](images/Nifi_pipeline.png?raw=true "Nifi Pipeline")