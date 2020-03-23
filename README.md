# Flink SQL 管理平台

> 基于tornado开发Flink SQL Client 管理SQL任务并提供实时调试功能web平台

## 依赖

1. Python3.6+
2. Flink 1.9+（推荐Flink1.10)已安装


## 安装

    pip install fsqlfly
 

## 部署

    fsqlfly webserver
 
  

## 效果展示

> 管理命名空间

![命名空间](images/namespace.png)

> 编写实时SQL

![实时SQL](images/sql.png)

> 实时动态调试SQL

![SQL调试](images/debug.png)


## 支持功能

- 管理命名空间
- 管理数据源
- 管理SQL函数
- 管理SQL编写及发布
- 动态调试SQL任务
- 导入关系数据库源
- 监控SQL任务运行并能自动重启


## TODO

- Flink集群任务总览
- SQL任务管理（当前可以通过Flink自带的管理界面管理）
