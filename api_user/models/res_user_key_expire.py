from typing import Optional, Union
from datetime import datetime
from odoo import models, fields

from ..datamodels.key_map import KeyMap

REDIS_FLAG = "key.expire.redis"

class KeyNotFound(Exception):
    pass

class ReachMaxCount(Exception):
    pass

class KeyExpired(Exception):
    pass

class KeyExpire(models.Model):
    _name = "res.users.key.expire"

    _description = "Key Expiration"

    key = fields.Char(index=1)
    expire_time = fields.Integer()
    count = fields.Integer(default=0)

    def _register_hook(self):
        self.pool.api_user_redis = eval(self.env["ir.config_parameter"].get_param(REDIS_FLAG, 'False'))
        return super()._register_hook()

    def add_key(self, key: str, expire_time: int, count: int = 0):
        if self.pool.api_user_redis:
            # TODO to store in redis
            ...
        else:
            self.create({
                "key": key,
                "expire_time": expire_time,
                "count": count
            })

    def _get_redis_key(self, key: str) -> Optional[KeyMap]:
        return None

    def _check_key(self, record: Optional[Union["KeyExpire", KeyMap]],  max_count: int):
        if not record:
            raise KeyNotFound("unknown key")
        if record.expire_time < datetime.utcnow().timestamp():
            raise KeyExpired("key already expired")
        if record.count and record.count >= max_count:
            raise ReachMaxCount("key has already been used")

    def validate_key(self, key: str, max_count: int = 1) -> bool:
        record = None
        if self.pool.api_user_redis:
            record = self._get_redis_key(key=key)
            self._check_key(record=record)
        else:
            record = self.search([("key", "=", key)])
            self._check_key(record=record, max_count=max_count)
            record.count += 1
        return True

    def schedule_delete_expire_keys(self):
        """This function will be run from Schedule Action.
        For redis, this function is not required
        """
        self.search([("expire_time", ">", datetime.utcnow().timestamp())]).unlink()
