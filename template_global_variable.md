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



#### Section: jdbc

 

Variable | Description | Default
---- | --- | ---
insert_primary_key| if false not insert primary key when in a sink table| false
add_read_partition_key| if true add read partition key in connector if database has a primary key and connector has no read field | false
read_partition_key| the read partition key if not have the primary key | None
auto_partition_bound| if true then get the read_partition_lower_bound and  read_partition_upper_bound from db | true
read_partition_num| partition num | 50
read_partition_fetch_size| Gives the reader a hint as to the number of rows that should be fetched if 0 then ignore | 0
read_partition_lower_bound| the smallest value of the first partition | 0
read_partition_upper_bound| the largest value of the last partition. | 50000


#### Section: system


Variable | Description | Default
---- | --- | ---
source_include|the source need load from all connection resource name|.*
source_exclude|the source exclude name from all connection resource name|''
target_database_format|the target database | {{ resource_name.database }}
target_table_format|the target tablename| {{ resource_name.name }}  
transform_name_format|the generate transform name format| {{ source_type }}2{{ target_type }}__{{ connector.name }}\__{{ resource_name.database }}\__{{ resource_name.name }}  
use_partition|if use partition |false
partition_name|if use partition |pt
partition_value|if use partition |{{ ds_nodash }}
overwrite|if overwrite |false



#### Section: kafka


Variable | Description | Default
---- | --- | ---
startup_mode|the kafka topic start up mode support (`earliest-offset`,`latest-offset`,`group-offsets` or `specific-offsets`)|latest-offset
topic|if set will overwrite the kafka connect topic|None




#### Section: canal


Variable | Description | Default
---- | --- | ---
mode| support `upsert`,`update`,`insert`,`delete`,`all` | `upsert`
process_time_enable| if true then kafka source will generate a process time in table|true
process_time_name| kafka source process time name(make true your table fields not contain it) |flink_process_time
rowtime_enable| if true then kafka source will generate a rowtime in table|true
rowtime_name| kafka source rowtime name(make true your table fields not contain it)  |mysql_row_time
rowtime_watermarks|kafka source rowtime watermarks default 5000 ms (5s)|5000
rowtime_from| kafka source rowtime field from  |MYSQL_DB_EXECUTE_TIME
binlog_type_name| mysql bin log type name  |MYSQL_DB_EVENT_TYPE
before_column_suffix| if mode contain `update` then will add to the field suffix|_before
after_column_suffix| if mode contain `update` then will add to the field suffix|_after
update_suffix| if mode contain `update` then will add to the field suffix|_updated
table_filter| use in canal filter table|.*\..*
canal_host| canal http web host | localhost
canal_port| canal http port | 11111
canal_username| canal username in config|null
canal_password| canal password in config|null
canal_destination| canal destination|null
canal_client_id| canal client id|null
 


PS: `mysql` bin log has three type, `update`,`insert` and `delete`,you can use `upsert` to convert
  all log to one kafka topic, also you can separate it into three topics. You can choose `all`
  or combine mode by `,` choose your canal sink type.  


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



