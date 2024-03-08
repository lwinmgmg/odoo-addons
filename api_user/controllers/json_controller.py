import logging
import json
from odoo.http import Response

_logger = logging.getLogger(__name__)


class HttpException(Exception):
    def __init__(
        self, details: dict | str, status: int, headers: dict = None, *args: object
    ) -> None:
        super().__init__(*args)
        self.headers = {"content-type": "application/json"}
        if isinstance(details, str):
            self.data = {"details": details}
        else:
            self.data = details
        self.status = status
        if headers:
            self.headers.update(headers)
        _logger.error(
            "Status: %s, Response : %s, Headers: %s",
            self.status,
            self.data,
            self.headers,
        )


class JsonController:
    @classmethod
    def rest_api(cls, func):
        def inner_func(*args, **kwargs):
            try:
                headers = {"content-type": "application/json"}
                res = func(*args, **kwargs)
                if isinstance(res, Response):
                    return res
                if kwargs.get("headers"):
                    headers.update(kwargs.get("headers"))
                return Response(json.dumps(res), headers=headers.items(), status=200)
            except HttpException as err:
                return Response(
                    json.dumps(err.data), headers=err.headers.items(), status=err.status
                )

        return inner_func
