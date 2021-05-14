#Streamsets Incremental
Streamsets tool is used to built incremental pipelines. 
A Pipeline is act as template and used to create Job for each table. 
All input to ingest data are passed as parameters while creating Job.
Below is screen shot of Pipeline.  
(Pipeline Name: NG_CDW_Incremental_Ingest_KUDU).

![GitHub Logo](docs/images/Streamsets_pipeline.png)


## Workflow
Streamsets incremental Pipeline/Job ingest records from source/DB2 to destination Kudu (current), Kudu (Historical), HDFS Avro (BackUp) and also send Telemetry to Kafka topics.
As per design, Streamsets job will run in streaming mode and ingest data in microbatch. Each batch is fetch based on last offset value. 

### Offset
Streamsets Incremental pipeline is driven by offset value. 
Basically offset is date and time or timestamp column of Kudu table which represent record's insert/update at source. 
Currently Date, Time and Timestamp is only supported data type. 
Offset value is passed as Run time parameter to Streamsets while creating job.  
Once job created and start running, Streamsets fetch records from source/DB2 based on initial offset (passed as runtime parameter). And after ingesting batch, Streamsets store the offset of last record in SCH.
To avoid partial updates or record inserted at same seconds, 60 seconds lag is added in offset range while querying source table. 
For e.g If current offset is 10-10-2020 10:10:10, then offset range to fetch next batch is from  10-10-2020 10:10:10 to (CURRENT_TIMESTAMP - 60 secs). So any updated/inserted record within last 60 secs won't be part of current batch but next.

## Streamsets Component

###JDBC Select Builder
This is custom built component used to fetch data from DB2 tables. 
Important inputs are:
1. DB2 JDBC URL/User/Password
2. Schema 
3. Database
4. Table
5. Primary Key
6. Offset Column
7. Select and Where clause
5. Initial Offset - Supported Data type is Date/Time/Timestamp.
6. Incremental Lag (in seconds) -  Delay ingest of latest record to avoid partial fetch. 

###Set NG Columns
Set Metadata columns required by Telemetry for e.g. Document ID, Instance ID, etc.
####Convert Date and Time to String
Preserves source Date/Time/Timestamp value but change data type to string.
###Trim CHAR Fields
Leading and trailing whitespaces are removed.
###Lowercase Columns Names
Converts all column names to lowercase. 
Convert null value into space if columns is part of Primary key. 
###Schema Drift - Remove Fields
This component contains Jython code which allows a programmatic way to handle changes in table schema. REMOVE_COLUMN is existing attribute can be used to define field names that need to be ignored during ingestion. TSV file is used to pass Runtime parameter to Streamsets. This external configuration provides more dynamic handling of Schema drift.
###Kudu
Kudu current - Upserts record to preserve only the most recent event changes.

Kudu History - Inserts record with timestamp in primary key which preserves all historical changes of the record. 
###HDFS/Avro
AVRO records stored to HDFS and an immutable record of the data.
###Pipeline Fragment - Telemetry
This component is used for Record level Telemetry. 
Prepare Telemetry message using Metadata fields(in JSON format) and then emits to kafka topic.

##Airflow Component
Airflow is used as Orchestration tool for Ingestion pipeline (Both Historical and Incremental). Airflow operator is used to manage life cycle of Streamsets Job.
###Streamsets SDK
Airflow operator uses Streamsets SDK to interact with SCH. All operations like Create, Start, Stop, etc. on Streamsets Pipeline/Job is executed usign SDK.
###Offset Utility
This utility is used to get latest offset from Kudu and then pass it as initial offset to Streamsets job while creating it.

###Configuration TSV

Runtime parameters required to create Streamsets Job is configured in TSV file. Below is Azure Repo link.

[Configured TSV](https://dev.azure.com/dastfs/NextGen/_git/Orchestration?path=%2Fairflow-orchestration%2Fngorch_config%2Finventory_cdw_tables.tsv)

Below are attributes of TSV file. 

```
database_name: Source Database
schema_name: Source Schema
table_name: Source table	
offset_columns	
primary_key_columns	
table_alias	
select_columns	
where_clause	
batch_size	
query_interval_seconds	
max_clob_chars	
max_blob_bytes	
incremental_lag_seconds	
remove_column	
binary_timestamp_column	
table_name_suffix	
logical_zone_name	
source_system_code	
data_source	
is_full_load: Y if only Historical load required else blank/empty	
is_event_table	
warehouse	
dest_schema: If Source to Destination cardinality is 1:*	
dest_table: If Source to Destination cardinality is 1:*	
commit_id: Override commit ID from Airflow configuration
```

Note that most of these parameter are passed only once while creating Job for first time. Once Job created, it store all these information internally. If needed, some of the parameter like initial offset, query interval, etc. can be overwritten while starting job.

Also current configuration only support Date, Time and Timestamp data type offset column. Development effort needed to support offset column of different data type.

###MetaData Table 
Metadata table is to keep the track of Streamsets Job created by Airflow Operator. 
For input table, Airflow Operator check this table for existing of Streamsets Job and create if not.

Database/schema: ng_orchestration_dev

Table: streamsets_jobs


 
Note: 
1. This table can contain only one entry for given database + Schema + Table.
2. Keep SCH in sync with this table. For e.g. if Job got deleted from SCH, then delete it from table too. Currently, there is no automated process to keep this table in sync with SCH.

###DAG
Below is DAG for one table. 

![GitHub Logo](docs/images/streamsets_dag.png)

