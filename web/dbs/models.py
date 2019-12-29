from django.db import models
from django.utils.html import escape, mark_safe
from web.settings import TIME_FORMAT

TABLE_TYPE = (
    ("sink-table", "输出表"),
    ("source-table", "输入表"),
)


class BaseModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    is_publish = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class Namespace(BaseModel):
    name = models.CharField("名字", max_length=256, db_index=True)
    info = models.CharField("介绍", max_length=2048, null=True, blank=True)
    avatar = models.CharField("图片地址", max_length=2048, null=True, blank=True)
    create_by = models.IntegerField("创建用户ID", default=0)

    class Meta:
        db_table = "namespace"
        unique_together = ["create_by", "name"]
        index_together = ["create_by", "name"]

    def __str__(self):
        return self.name

    __unicode__ = __str__

    def image_tag(self):
        return mark_safe('<img src="%s" height="50" />' % self.avatar) if self.avatar else '无上传图片'

    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    def _create_at(self):
        return self.create_at.strftime(TIME_FORMAT)

    _create_at.short_description = 'create'

    def _update_at(self):
        return self.update_at.strftime(TIME_FORMAT)

    _update_at.short_description = 'update'


class FileResource(BaseModel):
    unique_name = models.CharField("唯一名称", max_length=128)  # make true user give unique name
    info = models.CharField("介绍", max_length=1024, null=True, blank=True)
    real_path = models.CharField("文件路径", max_length=2048)
    create_by = models.IntegerField("创建用户ID", default=0)

    class Meta:
        db_table = "file_resource"
        unique_together = ["create_by", "unique_name"]
        index_together = ["create_by", "unique_name"]

    def __str__(self):
        return self.unique_name

    __unicode__ = __str__

    def _create_at(self):
        return self.create_at.strftime(TIME_FORMAT)

    _create_at.short_description = 'create'

    def _update_at(self):
        return self.update_at.strftime(TIME_FORMAT)

    _update_at.short_description = 'update'


class Resource(BaseModel):
    name = models.CharField("表名", max_length=256, db_index=True)
    info = models.CharField("介绍", max_length=2048, null=True, blank=True)
    typ = models.CharField("表类型", max_length=16, choices=TABLE_TYPE)
    yaml = models.TextField("其他信息(yaml格式)", default='')
    create_by = models.IntegerField("创建用户ID", default=0)
    namespace = models.ForeignKey(Namespace, on_delete=models.DO_NOTHING, null=True, blank=True)

    class Meta:
        db_table = "resource"

    def __str__(self):
        return self.name

    def _name_space_name(self):
        if self.namespace is not None:
            return self.namespace.name
        return "-"

    _name_space_name.short_description = "NAMESPACE"

    __unicode__ = __str__

    def _create_at(self):
        return self.create_at.strftime(TIME_FORMAT)

    _create_at.short_description = 'create'

    def _update_at(self):
        return self.update_at.strftime(TIME_FORMAT)

    _update_at.short_description = 'update'


class Functions(BaseModel):
    name = models.CharField("名字", max_length=256, db_index=True)
    function_from = models.CharField("来源", max_length=16, default="class")
    class_name = models.CharField("类名", max_length=256)
    constructor_config = models.CharField("构造器", max_length=2048)
    create_by = models.IntegerField("创建用户ID", default=0)
    resource = models.ForeignKey(FileResource, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "functions"
        unique_together = ["create_by", "name"]
        index_together = ["create_by", "name"]

    def __str__(self):
        return self.name

    __unicode__ = __str__

    def _create_at(self):
        return self.create_at.strftime(TIME_FORMAT)

    _create_at.short_description = 'create'

    def _update_at(self):
        return self.update_at.strftime(TIME_FORMAT)

    _update_at.short_description = 'update'

    def filename(self):
        return self.resource.name


class Transform(BaseModel):
    name = models.CharField("名字", max_length=256, db_index=True)
    info = models.CharField("介绍", max_length=2048, null=True, blank=True)
    sql = models.TextField("SQL")
    require = models.TextField("依赖链")
    yaml = models.TextField("其他信息(yaml格式)", default='')
    namespace = models.ForeignKey(Namespace, on_delete=models.DO_NOTHING, blank=True, null=True)
    create_by = models.IntegerField("创建用户ID", default=0)

    class Meta:
        db_table = "transform"
        unique_together = ["create_by", "name"]
        index_together = ["create_by", "name"]

    def __str__(self):
        return self.name

    __unicode__ = __str__

    def _create_at(self):
        return self.create_at.strftime(TIME_FORMAT)

    _create_at.short_description = 'create'

    def _update_at(self):
        return self.update_at.strftime(TIME_FORMAT)

    _update_at.short_description = 'update'

    def _name_space_name(self):
        if self.namespace is not None:
            return self.namespace.name
        return "-"


class ConnectionType:
    class MYSQL:
        name = 'mysql'
        suffix = '_ms'

    class KAFKA:
        name = 'kafka'
        suffix = '_kf'

    class HIVE:
        name = 'hive'
        suffix = '_hive'

    @classmethod
    def get_suffix(cls, name):
        for ob in [cls.MYSQL, cls.KAFKA, cls.HIVE]:
            if getattr(ob, 'name') == name:
                return getattr(ob, 'suffix')
        raise Exception("Not Find suffix")


class Connection(BaseModel):
    create_by = models.IntegerField("创建用户ID", default=0)
    name = models.CharField("名字", max_length=256)
    typ = models.CharField("类型", max_length=256)
    suffix = models.CharField("自主后缀", max_length=32, null=True, blank=True)
    username = models.CharField("用户名", max_length=64, null=True, blank=True)
    password = models.CharField("密码", max_length=256, null=True, blank=True)
    info = models.CharField("介绍", max_length=2048, null=True, blank=True)
    url = models.CharField("链接信息", max_length=2048)
    cache = models.TextField("缓存", null=True, blank=True)
    update_interval = models.IntegerField("更新间隔（秒）", default=3600)

    class Meta:
        db_table = "connection"
        unique_together = ["create_by", "name"]
        index_together = ["create_by", "name"]


class Relationship(BaseModel):
    create_by = models.IntegerField("创建用户ID", default=0)
    name = models.CharField("名字", max_length=256, db_index=True)
    info = models.CharField("介绍", max_length=2048, null=True, blank=True)
    cache = models.TextField("缓存", null=True, blank=True)
    typ = models.CharField("类型", max_length=256, choices=[('json', 'json'), ('yml', 'yml')], default='yml')
    config = models.TextField("配置")
    update_interval = models.IntegerField("更新间隔（秒）", default=3600)

    class Meta:
        db_table = 'relationship'
        unique_together = ["create_by", "name"]
        index_together = ["create_by", "name"]
