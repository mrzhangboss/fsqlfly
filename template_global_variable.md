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

### Connection Connector Format Variable

ps when `Type` = `connection` mean it's only generate in the connection 


Variable | Description | Type
---- | --- | ---



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



