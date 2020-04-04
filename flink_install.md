# Flink SQL Client 配置(推荐1.10.0 scala 版本为2.11)

- 下载[Flink版本](https://flink.apache.org/downloads.html)

- 下载[Connector](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/connect.html)

由于DNS污染目前官网的connector下载链接打不开，提供下面备用下载链接


### Connector

[Elasticsearch	6	flink-connector-elasticsearch6	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-elasticsearch6_2.11/1.10.0/flink-sql-connector-elasticsearch6_2.11-1.10.0.jar)
[Apache Kafka	0.8	flink-connector-kafka-0.8	Not available](#)
[Apache Kafka	0.9	flink-connector-kafka-0.9	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka-0.9_2.11/1.10.0/flink-sql-connector-kafka-0.9_2.11-1.10.0.jar)
[Apache Kafka	0.10	flink-connector-kafka-0.10	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka-0.9_2.11/1.10.0/flink-sql-connector-kafka-0.9_2.11-1.10.0.jar)
[Apache Kafka	0.11	flink-connector-kafka-0.11	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka-0.10_2.11/1.10.0/flink-sql-connector-kafka-0.10_2.11-1.10.0.jar)
[Apache Kafka	0.11+ (universal)	flink-connector-kafka	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka_2.11/1.10.0/flink-sql-connector-kafka_2.11-1.10.0.jar)
[HBase	1.4.3	flink-hbase	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-hbase_2.11/1.10.0/flink-hbase_2.11-1.10.0.jar)
[JDBC	 	flink-jdbc	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-jdbc_2.11/1.10.0/flink-jdbc_2.11-1.10.0.jar)

### Formats

[CSV (for Kafka)	flink-csv	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-csv/1.10.0/flink-csv-1.10.0-sql-jar.jar)
[JSON	flink-json	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-json/1.10.0/flink-json-1.10.0-sql-jar.jar)
[Apache Avro	flink-avro	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-avro/1.10.0/flink-avro-1.10.0-sql-jar.jar)

一键下载脚本

    cd /opt/flink-1.10.0/lib
    for p in '/flink-sql-connector-elasticsearch6_2.11/1.10.0/flink-sql-connector-elasticsearch6_2.11-1.10.0.jar' '/flink-sql-connector-kafka-0.9_2.11/1.10.0/flink-sql-connector-kafka-0.9_2.11-1.10.0.jar' '/flink-sql-connector-kafka-0.9_2.11/1.10.0/flink-sql-connector-kafka-0.9_2.11-1.10.0.jar' '/flink-sql-connector-kafka-0.10_2.11/1.10.0/flink-sql-connector-kafka-0.10_2.11-1.10.0.jar' '/flink-sql-connector-kafka_2.11/1.10.0/flink-sql-connector-kafka_2.11-1.10.0.jar' '/flink-hbase_2.11/1.10.0/flink-hbase_2.11-1.10.0.jar' '/flink-jdbc_2.11/1.10.0/flink-jdbc_2.11-1.10.0.jar' '/flink-csv/1.10.0/flink-csv-1.10.0-sql-jar.jar' '/flink-json/1.10.0/flink-json-1.10.0-sql-jar.jar' '/flink-avro/1.10.0/flink-avro-1.10.0-sql-jar.jar'
    do
      echo "begin download https://repo1.maven.org/maven2/org/apache/flink$p"
      wget "https://repo1.maven.org/maven2/org/apache/flink$p"
    done

## Hive 支持

依赖的`jar`包如下(hive 2.3.4)

		antlr4-runtime-4.5.jar        
		flink-connector-hive_2.11-1.9.0.jar
		antlr-runtime-3.5.2.jar        
		flink-hadoop-compatibility_2.11-1.9.0.jar
		datanucleus-api-jdo-4.2.4.jar  
		hive-exec-2.3.4.jar
		datanucleus-api-jdo-5.2.2.jar 
		javax.jdo-3.2.0-m3.jar
		datanucleus-core-4.1.17.jar   
		datanucleus-rdbms-4.1.9.jar    
		flink-shaded-hadoop-2-uber-2.7.5-8.0.jar
		jackson-core-2.8.11.ja

- [1.10.0 flink hive jar Google Driver 下载地址](https://drive.google.com/file/d/1hRit-IsX7zvkHloUg5S36czWKvpBgBtN/view?usp=sharing)
- 百度云提取码: e9c7 链接:  [1.10.0 flink hive 百度云下载地址](https://pan.baidu.com/s/1WFH4T7AiV31PrptTRTqzJA)
