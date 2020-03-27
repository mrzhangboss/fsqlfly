# Flink SQL Job Management Website

> require

1. python3.6+
2. flink 1.9.0+ installed


> install

    pip install fsqlfly
    

> run website
   
    fsqlfly webserver
    
    
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

> connection url detail in [FSQLFLY_DB_URL](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#connection-pool)

ps: the admin token value is `FSQLFLY_PASSWORD` md5 hex value, you can generate it by 

        import hashlib
        md5 = hashlib.md5()
        md5.update(b'password')
        token = md5.hexdigest()
