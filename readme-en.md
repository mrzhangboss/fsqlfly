# Flink SQL Job Management Website


## Display




> require

1. python3.6+
2. flink 1.9.0+ installed (need set `FSQLFLY_FLINK_BIN_DIR` in ~/.fsqlfly or in env)

ps: if you want run multi fsqlfly in one computer, you can set `FSQLFLY` in env , like

    export FSQLFLY=/path/where/you/like
    fsqlfly comand
    
you can generate a env template by `fsqlfly echoenv [filename]`


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

**require install [canal v1.1.4+](https://github.com/alibaba/canal)** 

    pip install fsqlfly[canal]
    fsqlfly canal --bootstrap_servers=localhost:9092 --canal_host=localhost --canal_port=11111 --canal_destination=demo \
    --canal_username=example --canal_password=pp --canal_client_id=1232
    
ps: you can use   `fsqlfly canal -h` get more information, you can set all varies in `.fsqlfly` file 
eg: 

    canal_username=root
    canal_destination=example
    canal_password=password
    canal_client_id=123
    bootstrap_servers=hadoop-1:9092,hadoop-2:9092
    canal_table_filter="database\\..*"
    canal_host=localhost
    

 
if you want to use canal data in flink , support load mysql database as mysql(both) |kafka(update and create)|elasticsearch(save) resource


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
    FSQLFLY_UPLOAD_DIR                upload dir                                                    ~/.fsqlfly_upload

    
                                                  

> connection url detail in [FSQLFLY_DB_URL](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#database-url)

ps: the admin token value is `FSQLFLY_PASSWORD` md5 hex value, you can generate it by 

        import hashlib
        md5 = hashlib.md5()
        md5.update(b'password')
        token = md5.hexdigest()


if you want control all flink sql job start and stop by api, you can add token in url or header without login


## API

> need login by token(in request params `token`)

- jobs

        url: /api/job
        method: get
        

- job control 

      url: /api/job/<mode(start|stop|restart)>/<id>
      method: post

**Beta** you can set `pt` in request body(json format), then will create a unique job 
name for job, if you sql need other format value, we support `jinja2` format 
eg: `insert into tablea select * from table where pt_field = {{ pt }};`
you can send `pt` value in request body.I recommend you control daily job by `airflow`.
 
 


