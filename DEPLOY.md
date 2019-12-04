## 复制最新代码

    git clone https://github.com/mrzhangboss/FlinkSQLPlatform.git
    cd FlinkSQLPlatform
    git fetch origin back-end
    git checkout back-end
    

## 搭建环境

1. 编译前端文件(分支frontend），复制到`web/static`文件目录
2. 复制环境变量, `cp web/.env.template web/.env`
3. 初始化django环境, `cd web && python manage.py migrate`
4. 运行django 后台,`python manage.py runserver 0.0.0.0:8080`
5. 运行调试后端`cd ../terminal && python named.py`



## 从数据库中导入数据源

> 当前支持mysql, kafka, elasticsearch

    cd web 
    python manage.py load_mysql_resource --host localhost --database db --namespace namespace \
    --category mysql --tables "*" --kafka-bootstrap "localhost:9092" --es-hosts http://localhost:9200 \
    --port 3306 --password xxx --username root
    
    
 
## 支持消费Canal导入数据

启动[Canal Instance](https://github.com/alibaba/canal)

在.env 中填写

    canal_host = 'localhost'
    canal_port = 11111
    canal_username = root
    canal_destination = example
    canal_password = xxxx
    canal_client_id = 12123

canal_username 增量MySQL数据库用户名
canal_password 增量MySQL数据库密码

    cd web
    python manage.py canal_consumer
    
    
# 支持功能

1. yml 文件以及SQL语句都支持[jinja2](https://jinja.palletsprojects.com/en/2.10.x/)模板语法，推荐使用`Airflow`进行调度

调度API为：
    
        url: /api/jobs/{job_name}/{method}
        method: POST

支持`restart`、`stop`、`start`三种模式，如果带有参数`pt`，可以用来区分同一SQL任务不同脚本
由于使用Cache缓存，所以Get请求都会有10分钟的缓冲，虽然没有限制请求方法所以推荐使用`POST`来进行请求，如果发送的`json`里面包含变量，会传递给模板到`SQL`和`yaml`配置文件中

2. 支持定时监控集群`SQL`job,只要把`Transform`设置为发布可用就可以一直运行，前提是配置好了`Flink`任务

