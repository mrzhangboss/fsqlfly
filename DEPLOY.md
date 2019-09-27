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

