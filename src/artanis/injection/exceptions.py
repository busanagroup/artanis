#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Busana Apparel Group. All rights reserved.
#
# This product and it's source code is protected by patents, copyright laws and
# international copyright treaties, as well as other intellectual property
# laws and treaties. The product is licensed, not sold.
#
# The source code and sample programs in this package or parts hereof
# as well as the documentation shall not be copied, modified or redistributed
# without permission, explicit or implied, of the author.
#
# This module is part of Artanis Enterprise Platform and is released under
# the Apache-2.0 License: https://www.apache.org/licenses/LICENSE-2.0
import typing as t

if t.TYPE_CHECKING:
    from artanis.injection.components import Component
    from artanis.injection.resolver import Parameter

__all__ = ["ComponentError", "ComponentNotFound"]


class InjectionError(Exception): ...


class ComponentError(InjectionError): ...


class ComponentNotFound(ComponentError):
    def __init__(
        self,
        parameter: "Parameter",
        component: "Component | None" = None,
        function: t.Callable | None = None,
    ):
        self.parameter = parameter
        self.component = component
        self.function = function

    def __str__(self) -> str:
        msg = f"No component able to handle parameter '{self.parameter.name}'"
        if self.component:
            msg += f" in component '{self.component.__str__()}'"
        if self.function:
            msg += f" for function '{self.function.__name__}'"

        return msg
