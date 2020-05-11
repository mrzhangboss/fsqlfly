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
   
    fsqlfly webserver [--jobdaemon]
    
ps: if you want daemon all flink sql job(need set publish and available), add `--jobdaemon` in commands

    
> reset database (warning it'll delete all data)
    
    fsqlfly resetdb
    


> support canal consumer(load mysql log data to kafka)

**require install [canal v1.1.4+](https://github.com/alibaba/canal)** 

    pip install fsqlfly[canal]

    fsqlfly runcanal [name or id]

# settings

you can change by write in `env file` (~/.fsqlfly) or just in environment variables (`eg: export name=value`)


Name | Description|Default
---- | --- | ---
FSQLFLY_PASSWORD|admin password(if not set use a random password)|password
FSQLFLY_DB_URL|database connection url(if you set then other is ignore) |None
FSQLFLY_STATIC_ROOT|the dir of static file(if not set then it will be fsqlfly/static) |None
FSQLFLY_FLINK_BIN_DIR|the dir of flink bin dir |/opt/flink/bin
FSQLFLY_FLINK_MAX_TERMINAL|the max value of living terminal  |1000
FSQLFLY_DEBUG| set web debug(if set then set True else False)   |None
FSQLFLY_DEBUG| set web debug(if set then set True else False)   |None
FSQLFLY_WEB_PORT|set http port   |8082
FSQLFLY_FINK_HOST|  flink REST api host  | http://localhost:8081
FSQLFLY_JOB_DAEMON_FREQUENCY| each job check damon time second           | 30
FSQLFLY_JOB_DAEMON_MAX_TRY_ONE_DAY| each job maximum try times in one day            | 3
FSQLFLY_JOB_LOG_DIR| flink job damon log file            | /tmp/fsqlfly_job_log
FSQLFLY_UPLOAD_DIR| upload dir            | ~/.fsqlfly_upload
FSQLFLY_SAVE_MODE_DISABLE| if set then support delete or otherwise            | False 
FSQLFLY_MAIL_ENABLE| send email or not |false
FSQLFLY_MAIL_HOST| smt email host|None
FSQLFLY_MAIL_USER| smt email user|None
FSQLFLY_MAIL_PASSWORD| smt email password |None
FSQLFLY_MAIL_RECEIVERS| smt email receivers sep by ,|None

   

    
    
                                                  

> connection url detail in [FSQLFLY_DB_URL](https://docs.sqlalchemy.org/en/13/core/engines.html)

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

      url: /api/transform/<mode(status|start|stop|restart)>/<id or job name>
      method: post


**Beta** you can set `pt` in request body(json format), then will create a unique job 
name for job, if you sql need other format value, we support `jinja2` format 
eg: `insert into tablea select * from table where pt_field = {{ pt }};`
you can send `pt` value in request body.I recommend you control daily job by `airflow`.
If you want kill all `pt` job add `kill_all_pt` in request json body.

PS: `pt` only can contain '0-9a-zA-Z_-' 
PS: `status` api if no `last_run_job_id` or multi running job , api will return `FAILED`  


## Airflow Support

> use dag operator in `fsqlfly.airflow_plugins.FSQLFlyOperator`

example:

    from airflow.models import DAG
    from fsqlfly.airflow_plugins import FSQLFlyOperator

    dag = DAG(
        dag_id='flink_hive_process',
        default_args=args,
        schedule_interval="2 1 * * *",
        dagrun_timeout=timedelta(minutes=60),
        max_active_runs=8,
        concurrency=8
    )
    
    data = dict(pt="{{ ds_nodash }}")
    http_conn_id = "fsqlplatform"
    token = '{{ var.value.fsqlfly_token }}'
    start_flink_job = FSQLFlyOperator(
        task_id='fink_job',
        job_name='flik_run_in_fsql_fly',
        token=token,
        http_conn_id=http_conn_id,
        data=data,
        dag=dag,
        method='start',  # support restart | start | stop  
        daemon=True,
        parallelism=0,   # if parallelism set not zero then will control the max running job one time
        poke_interval=5,
    )

    
`token`: fsqlfly token, you can real token, also you can save in `variable` in airflow
`HOST`: airflow connection id , see more in [detail](https://airflow.apache.org/docs/stable/howto/connection/index.html)
`data`: args in flink job

if you want control `connector` by airflow you can use `fsqlfly.airflow_plugins.FSQLFlyConnectorOperator` same usage as upper.



## Quick Start


1. unzip Flink 1.10.0 to /opt/flink
2. `pip install fsqlfly`
3. `fsqlfly echoenv ~/.fsqlfly`
4.  change the value `FSQLFLY_FLINK_BIN_DIR` in `~/.fsqlfly` to your flink bin dir  like `/opt/flink/bin`
5.  `fsqlfly initdb`
6. `fsqlfly runwebserver`
7. open your browser in `http://localhost:8082` the password is `password`
