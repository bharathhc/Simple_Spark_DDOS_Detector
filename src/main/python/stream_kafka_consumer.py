from pyspark.sql import SparkSession
from pyspark.sql.functions import count, col, regexp_extract, to_timestamp
import configparser

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Read kafka properties from config.ini
    jars = config['DEPENDENCIES']['jar_dependencies']
    bootstrap_server = config['KAFKA_PROPERTIES']['kafka_bootstrap_servers']
    topic = config['KAFKA_PROPERTIES']['kafka_topic']

    spark = SparkSession \
        .builder \
        .config('spark.jars', jars) \
        .appName("File Streaming Demo") \
        .master("local[3]") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .config("spark.sql.shuffle.partitions", 3) \
        .getOrCreate()

    # Minimum number of times a host should request the server in a second to consider as DDOS attack
    threshold = 5

    # Reading from Kafka Topic
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", bootstrap_server) \
        .option("subscribe", topic) \
        .option("startingOffsets", "earliest") \
        .load()

    # Casting the data type of key and value columns to String
    df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

    # Regular Expression to extract information from Text data
    host_pattern = r'(^\S+\.[\S+\.]+\S+)\s'
    ts_pattern = r'^.*\[(\d\d/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})'
    method_uri_protocol_pattern = r'\"(\S+)\s(\S+)\s*(\S*)\"'
    status_pattern = r'\s(\d{3})\s'
    content_size_pattern = r'\s(\d+)$'

    # Extracting host, timestamp etc information from Text data
    logs_df = df.select(regexp_extract('value', host_pattern, 1).alias('host'),
                        regexp_extract('value', ts_pattern, 1).alias('timestamp'),
                        regexp_extract('value', method_uri_protocol_pattern, 1).alias('method'),
                        regexp_extract('value', method_uri_protocol_pattern, 2).alias('endpoint'),
                        regexp_extract('value', method_uri_protocol_pattern, 3).alias('protocol'),
                        regexp_extract('value', status_pattern, 1).cast('integer').alias('status'),
                        regexp_extract('value', content_size_pattern, 1).cast('integer').alias('content_size'))

    logs_df.printSchema()
    logs_df = logs_df.withColumn('timestamp', to_timestamp(logs_df['timestamp'], 'dd/MMM/yyyy:HH:mm:ss'))

    grouped_df = logs_df.withWatermark('timestamp', '1 minute').groupBy('host', 'timestamp').agg(count('host')
                                                                                                 .alias('total_count'))

    # Count of requests made each second by a host
    # grouped_df = logs_df.groupBy('host', 'timestamp').agg(count('host').alias('total_count'))
    result_host = grouped_df.filter(col('total_count') > threshold).select('host').distinct()

    writer_query = result_host.writeStream \
        .format("csv") \
        .queryName("csv Writer") \
        .outputMode("append") \
        .option("path", "results") \
        .option("checkpointLocation", "chk-point-dir") \
        .start()

    # # Writing to console sink
    # writer_query = result_host.writeStream \
    #     .format("console") \
    #     .outputMode("complete") \
    #     .option("checkpointLocation", "chk-point-dir") \
    #     .start()

    writer_query.awaitTermination()
