from django.db import models

TABLE_TYPE = (
    ("sink-table", "输出表"),
    ("source-table", "输入表"),
)


class Namespace(models.Model):
    name = models.CharField("名字", max_length=256, db_index=True)
    info = models.CharField("介绍", max_length=2048, null=True, blank=True)
    avatar = models.CharField("图片地址", max_length=2048, null=True, blank=True)
    create_by = models.IntegerField("创建用户ID", default=0)
    is_deleted = models.BooleanField(default=False)
    is_publish = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = "namespace"
        unique_together = ["create_by", "name"]
        index_together = ["create_by", "name"]


class FileResource(models.Model):
    unique_name = models.CharField("唯一名称", max_length=128)  # make true user give unique name
    info = models.CharField("介绍", max_length=1024, null=True, blank=True)
    real_path = models.CharField("文件路径", max_length=2048)
    create_by = models.IntegerField("创建用户ID", default=0)
    is_publish = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = "file_resource"
        unique_together = ["create_by", "unique_name"]
        index_together = ["create_by", "unique_name"]


class Resource(models.Model):
    name = models.CharField("表名", max_length=256, db_index=True)
    info = models.CharField("介绍", max_length=2048, null=True, blank=True)
    typ = models.CharField("表类型", max_length=16, choices=TABLE_TYPE)
    yaml = models.TextField("其他信息(yaml格式)", default='')
    create_by = models.IntegerField("创建用户ID", default=0)
    is_available = models.BooleanField(default=True)
    is_publish = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    namespace = models.ForeignKey(Namespace, on_delete=models.DO_NOTHING, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = "resource"
        unique_together = ["create_by", "name"]
        index_together = ["create_by", "name"]


PROPERTY_CATEGORY = (
    ("connector", "连接器"),
    ("format", "格式器"),
    ("schema", "SQL格式")
)

PART_TYPE = (
    # connector type
    ("kafka", "kafka"),
    ("filesystem", "filesystem"),
    ("elasticsearch", "Elasticsearch"),

    # format type
    ("csv", "csv"),
    ("json", "json"),
    ("avro", "avro"),
)


class Functions(models.Model):
    name = models.CharField("名字", max_length=256, db_index=True)
    function_from = models.CharField("来源", max_length=16, default="class")
    class_name = models.CharField("类名", max_length=256)
    constructor_config = models.CharField("构造器", max_length=2048)
    create_by = models.IntegerField("创建用户ID", default=0)
    resource = models.ForeignKey(FileResource, on_delete=models.DO_NOTHING)
    is_publish = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = "functions"
        unique_together = ["create_by", "name"]
        index_together = ["create_by", "name"]


class Transform(models.Model):
    name = models.CharField("名字", max_length=256, db_index=True)
    info = models.CharField("介绍", max_length=2048, null=True, blank=True)
    sql = models.TextField("SQL")
    require = models.TextField("依赖链")
    sink = models.ForeignKey(Resource, on_delete=models.DO_NOTHING, blank=True, null=True)
    namespace = models.ForeignKey(Namespace, on_delete=models.DO_NOTHING, blank=True, null=True)
    is_used_as_view = models.BooleanField(default=False)
    use_self = models.BooleanField(default=False)
    create_by = models.IntegerField("创建用户ID", default=0)
    is_publish = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = "transform"
        unique_together = ["create_by", "name"]
        index_together = ["create_by", "name"]
