# Flink SQL Job Management Website

> require

1. python3.6+
2. flink 1.9.0+ installed (need set `FSQLFLY_FLINK_BIN_DIR` in ~/.fsqlfly or in env)


> install

    pip install fsqlfly
    
> init database

    fsqlfly initdb 

> run website
   
    fsqlfly webserver
    
> reset database (warning it'll delete all data)
    
    fsqlfly webserver
    
> daemon all flink sql job

    fsqlfly jobdaemon

> support canal consumer(load mysql log data to kafka)

    pip install fsqlfly[canal]
    fsqlfly canal --bootstrap_servers=localhost:9092 --canal_host=localhost --canal_port=10000 --canal_destination=demo \
    --canal_username=example --canal_password=pp --canal_client_id=12312412 --canal_table_filter=.*
    
you can use   `fsqlfly canal -h` get more information

 
if you want to read this in kafka mysql  
support load mysql database as mysql(both) |kafka(update and create)|elasticsearch(save) resource


    pip install fsqlfly[canal]
    fsqlfly loadmysql --host=localhost --database=fsqlfly --namespace=demo --category=kafka --tables=* --password=password --username=root
    
you can set category as (kafka,mysql,es), it will create resource automatic by database  

    


# settings

you can change by write in `env file` (~/.fsqlfly) or just in environment variables (`eg: export name=value`)

    
        name               express                     default
    FSQLFLY_PASSWORD       admin password(if not set use a radom password)               password
    FSQLFLY_DB_URL          database connection url(if you set then other is ignore)                            None
    FSQLFLY_DB_TYPE        use db type support: [sqlite|mysql|postgresql]            sqlite
    FSQLFLY_DB_FILE         sqlite db file name             db.sqlite3
    FSQLFLY_DATABASE         database                       test        
    FSQLFLY_DB_PASSWORD         database passowrd                       xxx        
    FSQLFLY_DB_USER         database user                       root        
    FSQLFLY_DB_PORT         database port                       3306
    FSQLFLY_STATIC_ROOT     the dir of static file(if not set then it will be fsqlfly/static)  None
    FSQLFLY_FLINK_BIN_DIR     the dir of flink bin dir                                     /opt/flink/bin
    FSQLFLY_FLINK_MAX_TERMINAL   the max value of living terminal                             1000
    FSQLFLY_DEBUG                   set web debug(if set then set True else False)                None
    FSQLFLY_WEB_PORT              set http port                                             8082
    FSQLFLY_FINK_HOST              flink resetful api host                                   http://localhost:8081
    FSQLFLY_JOB_DAEMON_FREQUENCY              each job check damon time second                                    30
    FSQLFLY_JOB_DAEMON_MAX_TRY_ONE_DAY              each job maxium try times in one day                                    3
    FSQLFLY_JOB_LOG_DIR              flink job damon log file                                     /tmp/fsqlfly_job_log
    
    
                                                  

> connection url detail in [FSQLFLY_DB_URL](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#database-url)

ps: the admin token value is `FSQLFLY_PASSWORD` md5 hex value, you can generate it by 

        import hashlib
        md5 = hashlib.md5()
        md5.update(b'password')
        token = md5.hexdigest()
