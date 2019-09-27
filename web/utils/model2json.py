# -*- coding: utf-8 -*-
import re
from django.core.serializers.json import Serializer as Base
from collections import OrderedDict


class Serializer(Base):
    """Delete (`[` in begin `]` in the end) in output and change underline field name to camel

    """

    def start_serialization(self):
        self._init_options()

    def end_serialization(self):
        if self.options.get("indent"):
            self.stream.write("\n")
        if self.options.get("indent"):
            self.stream.write("\n")

    __CAMEL_PATTERN = re.compile(r"(?<=[a-z\d])(_[a-z])")

    def _rename(self, name: str):
        return self.__CAMEL_PATTERN.sub(lambda x: x.group()[1].upper(), name)

    def rename_column(self, data: dict):
        _r = self._rename
        _c = self.rename_column

        return {_r(k): ([_c(x) for x in v] if isinstance(v, list) else (_c(v) if isinstance(v, dict) else v))
                for k, v in data.items()}

    def get_dump_object(self, obj):
        data = OrderedDict([('model', str(obj._meta))])
        if not self.use_natural_primary_keys or not hasattr(obj, 'natural_key'):
            data["pk"] = self._value_from_field(obj, obj._meta.pk)
        fields = self.rename_column(self._current)
        data['fields'] = fields
        return data
