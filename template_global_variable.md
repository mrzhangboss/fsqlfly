# Template Global Variable

> see more detail in [jina2](https://jinja.palletsprojects.com/en/master/templates/#variables)
> 
>support airflow all [macros](https://airflow.apache.org/docs/stable/macros-ref.html)

 
### Generate Version Cache



Variable | Description
---- | ---
{{ version }} |  the generate version object
{{ connection }} | the generate version connection field (version.connection)  
{{ template }} |  the generate version template field (version.template)
{{ resource_name }} |  the generate version resource_name field (version.resource_name)

### Connection And ResourceName Config Format Variable

`ResourceName` config inherit his `Connection` config.The `Config` format is `Configuration`.

eg:

        [DEFAULT]
        ServerAliveInterval = 45
        Compression = yes
        CompressionLevel = 9
        ForwardX11 = yes



#### Section: db

 

Variable | Description | Default
---- | --- | ---
insert_primary_key| if false not insert primary key when in a sink table| false
add_read_partition_key| if true add read partition key in connector if database has a primary key and connector has no read field | false
read_partition_num| partition num | 50
read_partition_fetch_size| Gives the reader a hint as to the number of rows that should be fetched if 0 then ignore | 0
read_partition_lower_bound| the smallest value of the first partition | 0
read_partition_upper_bound| the largest value of the last partition. | 50000


#### Section: kafka


Variable | Description | Default
---- | --- | ---

process_time_enable| if true then kafka source will generate a process time in table|true
process_time_name| kafka source process time name(make true your table fields not contain it) |flink_process_time
rowtime_enable| if true then kafka source will generate a rowtime in table|true
rowtime_name| kafka source rowtime name(make true your table fields not contain it)  |row_time
rowtime_from| kafka source rowtime field from  |MYSQL_DB_EXECUTE_TIME






### Template And Version Config Field Format

Variable | Description|type
---- | --- | ---
exclude| the field not be add in final version(sep by ',' and support regex)| str
include| the field'll be add in final version(sep by ',' and support regex)|str
schema|add into final version|list format (name: type)
format|replace final version format|yml format 
update-mode|if add then will replace default update-mode field|str
query|if add then will replace default query field|str
history-table|if add then will replace default history-table field|str
primary-key|if add then will replace default primary-key field|str
time-attribute|if add then will replace default time-attribute field|str



