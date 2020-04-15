# Flink SQL Client 配置(推荐1.10.0 scala 版本为2.11)

- 下载[Flink版本](https://flink.apache.org/downloads.html)

- 下载[Connector](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/connect.html)

由于DNS污染目前官网的connector下载链接打不开，提供下面备用下载链接


### Connector

- [Elasticsearch	6	flink-connector-elasticsearch6	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-elasticsearch6_2.11/1.10.0/flink-sql-connector-elasticsearch6_2.11-1.10.0.jar)
- [Apache Kafka	0.8	flink-connector-kafka-0.8	Not available](#)
- [Apache Kafka	0.9	flink-connector-kafka-0.9	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka-0.9_2.11/1.10.0/flink-sql-connector-kafka-0.9_2.11-1.10.0.jar)
- [Apache Kafka	0.10	flink-connector-kafka-0.10	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka-0.10_2.11/1.10.0/flink-sql-connector-kafka-0.10_2.11-1.10.0.jar)
- [Apache Kafka	0.11	flink-connector-kafka-0.11	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka-0.11_2.11/1.10.0/flink-sql-connector-kafka-0.11_2.11-1.10.0.jar)
- [Apache Kafka	0.11+ (universal)	flink-connector-kafka	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka_2.11/1.10.0/flink-sql-connector-kafka_2.11-1.10.0.jar)
- [HBase	1.4.3	flink-hbase	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-hbase_2.11/1.10.0/flink-hbase_2.11-1.10.0.jar)
- [JDBC	 	flink-jdbc	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-jdbc_2.11/1.10.0/flink-jdbc_2.11-1.10.0.jar)

### Formats

- [CSV (for Kafka)	flink-csv	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-csv/1.10.0/flink-csv-1.10.0-sql-jar.jar)
- [JSON	flink-json	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-json/1.10.0/flink-json-1.10.0-sql-jar.jar)
- [Apache Avro	flink-avro	Download](https://repo1.maven.org/maven2/org/apache/flink/flink-avro/1.10.0/flink-avro-1.10.0-sql-jar.jar)

一键下载脚本（不包含kafka依赖，请单独下载具体使用的kafka版本，注意不要下载多个kafka版本，目前不支持一个集群使用多版本kafka）

    cd /opt/flink-1.10.0/lib
    for p in '/flink-sql-connector-elasticsearch6_2.11/1.10.0/flink-sql-connector-elasticsearch6_2.11-1.10.0.jar' '/flink-hbase_2.11/1.10.0/flink-hbase_2.11-1.10.0.jar' '/flink-jdbc_2.11/1.10.0/flink-jdbc_2.11-1.10.0.jar' '/flink-csv/1.10.0/flink-csv-1.10.0-sql-jar.jar' '/flink-json/1.10.0/flink-json-1.10.0-sql-jar.jar' '/flink-avro/1.10.0/flink-avro-1.10.0-sql-jar.jar'
    do
      echo "begin download https://repo1.maven.org/maven2/org/apache/flink$p"
      wget "https://repo1.maven.org/maven2/org/apache/flink$p"
    done


**Option** (JDBC Driver)

- MySQL	mysql	mysql-connector-java	[Download](https://repo1.maven.org/maven2/mysql/mysql-connector-java/)
- PostgreSQL	org.postgresql	postgresql	[Download](https://jdbc.postgresql.org/download.html)
- Derby	org.apache.derby	derby	[Download](http://db.apache.org/derby/derby_downloads.html)


## Hive 支持



请参考下面这个项目 

[flink-hive-dependence](https://github.com/mrzhangboss/flink-hive-dependence)
