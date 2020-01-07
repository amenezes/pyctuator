import dataclasses
import json
from typing import Dict

from flask import Blueprint, request
from flask import Flask

from pyctuator.pyctuator_impl import PyctuatorImpl
from pyctuator.pyctuator_router import PyctuatorRouter


class FlaskPyctuator(PyctuatorRouter):

    def __init__(
            self,
            app: Flask,
            pyctuator_impl: PyctuatorImpl
    ):
        super().__init__(app, pyctuator_impl)
        path_prefix = pyctuator_impl.pyctuator_endpoint_path_prefix
        flask_blueprint: Blueprint = Blueprint("flask_blueprint", "pyctuator", )

        @flask_blueprint.route(path_prefix)
        # pylint: disable=unused-variable
        def get_endpoints() -> Dict:
            return dataclasses.asdict(self.get_endpoints_data())

        @flask_blueprint.route(path_prefix + "/env")
        # pylint: disable=unused-variable
        def get_environment() -> Dict:
            return dataclasses.asdict(pyctuator_impl.get_environment())

        @flask_blueprint.route(path_prefix + "/info")
        # pylint: disable=unused-variable
        def get_info() -> Dict:
            return dataclasses.asdict(pyctuator_impl.app_info)

        @flask_blueprint.route(path_prefix + "/health")
        # pylint: disable=unused-variable
        def get_health() -> Dict:
            return dataclasses.asdict(pyctuator_impl.get_health())

        @flask_blueprint.route(path_prefix + "/metrics")
        # pylint: disable=unused-variable
        def get_metric_names() -> Dict:
            return dataclasses.asdict(pyctuator_impl.get_metric_names())

        @flask_blueprint.route(path_prefix + "/metrics/<metric_name>")
        # pylint: disable=unused-variable
        def get_metric_measurement(metric_name: str) -> Dict:
            return dataclasses.asdict(pyctuator_impl.get_metric_measurement(metric_name))

        # Retrieving All Loggers
        @flask_blueprint.route(path_prefix + "/loggers")
        # pylint: disable=unused-variable
        def get_loggers() -> Dict:
            return dataclasses.asdict(pyctuator_impl.logging.get_loggers())

        @flask_blueprint.route(path_prefix + "/loggers/<logger_name>", methods=['POST'])
        # pylint: disable=unused-variable
        def set_logger_level(logger_name: str) -> Dict:
            request_dict = json.loads(request.data)
            pyctuator_impl.logging.set_logger_level(logger_name, request_dict.get("configuredLevel", None))
            return {}

        @flask_blueprint.route(path_prefix + "/loggers/<logger_name>")
        # pylint: disable=unused-variable
        def get_logger(logger_name: str) -> Dict:
            return dataclasses.asdict(pyctuator_impl.logging.get_logger(logger_name))

        @flask_blueprint.route(path_prefix + "/threaddump")
        @flask_blueprint.route(path_prefix + "/dump")
        # pylint: disable=unused-variable
        def get_thread_dump() -> Dict:
            return dataclasses.asdict(pyctuator_impl.get_thread_dump())

        app.register_blueprint(flask_blueprint)