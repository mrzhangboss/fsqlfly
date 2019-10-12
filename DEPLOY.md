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
    
    
 
