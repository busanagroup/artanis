import typing as t

from artanis import types
from artanis.abc.workers import AbstractWorker
from artanis.injection import Component

if t.TYPE_CHECKING:
    from artanis.injection import Parameter


__all__ = ["WorkerComponent"]


class WorkerComponent(Component):
    def __init__(self, worker: AbstractWorker):
        self.worker = worker

    def can_handle_parameter(self, parameter: "Parameter") -> bool:
        return parameter.annotation is self.worker.__class__

    def resolve(self, scope: types.Scope):
        self.worker.app = scope["root_app"]
        return self.worker
