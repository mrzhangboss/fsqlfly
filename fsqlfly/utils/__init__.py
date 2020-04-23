# -*- coding:utf-8 -*-
import attr
from typing import Any, Optional


@attr.s
class DBRes:
    data: Any = attr.ib()
    code: int = attr.ib(default=200)
    msg: Optional[str] = attr.ib(default=None)
    success: bool = attr.ib(default=True)
