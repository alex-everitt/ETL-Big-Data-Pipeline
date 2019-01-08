# HortonWorks SandBox with HDP 2.6.4
#spark-submit ./SparkRDD_Demo.py

from pyspark import SparkConf, SparkContext, sql
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from datetime import datetime
import sys

#This function maps entries to the key "Error" or "Warn" depending on line contents
def Mapper(line):
        data = line.split(" ")#split line by tabs to extract all words as tokens
        type = "Warn"#Initialize key to "Warn"
		#For each word in the line, check if it matches a keyword
        for word in data:
                if word == "Error" or word == "error:" or word == "error" or word == "fail":
                        type = "Error"#Set key to "Error" is it is found on the line
        ##Return the Key along with a value of 1.0, corresponding to the count of lines
        return (type,(1.0))

#This function publishes records to the "Results" topic on Kafka
def publishToKafka(message):
	# get records from rdd
	records = message.collect()
	for record in records:
			# publish record to topic "Results"
			producer.send("Results", str(record))
			producer.flush()
				
if __name__ == "__main__":
		#get current time
		start_time = datetime.now()
		#format timestamp 
        timestamp = start_time.strftime("%d-%m-%Y %H:%M%S")

        #create SparkContext
        conf = SparkConf().setAppName("Cisc432Spark")
        sc = SparkContext(conf = conf)
		#Create streaming conext with 60 second window
		ssc = StreamingContext(sc, 60)
		
		#Set up Kafka connection
		kafkaParams = { "bootstrap.servers": "sandbox-hdp.hortonworks.com:6667" }
        # create a DStream to subscribe to Warn and Error topics
        kafkaStream = KafkaUtils.createDirectStream(ssc, ["Warn", "Error"], kafkaParams)

		#Map lines according to Mapper function
		lines = kafkaStream.map(Mapper)
		# Reduce lines by key over a 60 second window sliding every 5 seconds
        reduced = keyWordPairs.reduceByKeyAndWindow(lambda a, b: a + b, 60, 5)
		
		#Take RDD entries (there will only be 2 because there are only 2 possible keys)
        output = reduced.take(2)
		#Format and publish to Kafka
        publishToKafka("Warning:\t%d\t%s" % (output[0][1],timestamp))
        publishToKafka("Error:\t%d\t%s" % (output[1][1],timestamp))
		
		# set checkpoint directory for window operations
		ssc.checkpoint("./checkpoint")
		
		#Start streaming job
		ssc.start()
		ssc.awaitTermination()
