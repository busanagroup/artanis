#
# Copyright (c) 2018 Busana Apparel Group. All rights reserved.
#
# This product and it's source code is protected by patents, copyright laws and
# international copyright treaties, as well as other intellectual property
# laws and treaties. The product is licensed, not sold.
#
# The source code and sample programs in this package or parts hereof
# as well as the documentation shall not be copied, modified or redistributed
# without permission, explicit or implied, of the author.
#

__author__ = 'jaimy'
__version__ = '2.0'
__copyright__ = 'Copyright (c) 2025 Busana Apparel Group'

from artanis.sqlentity.sqlorm import *


class efurob(Entity):
    """
    User Access RPC Module Object
    """

    urmusrnm = Field(String(24), label='User name', primary_key=True)
    urmobjnm = Field(String(32), label='Object Name', primary_key=True)
    urmfncnm = Field(String(48), label='Function Name', primary_key=True)
    urmoaudt = Field(Numeric(8, 0), label='Audit date')
    urmoautm = Field(Numeric(6, 0), label='Audit time')
    urmoauus = Field(String(24), label='Audit user')

    @classmethod
    async def check_public_access(cls, service_name: str, func_name: str):
        return True if (await cls.get_by(urmusrnm='*', urmobjnm='*', urmfncnm='*')) is not None else \
            True if (await cls.get_by(urmusrnm='*', urmobjnm='*', urmfncnm=func_name)) is not None else \
                True if (await cls.get_by(urmusrnm='*', urmobjnm=service_name, urmfncnm='*')) is not None else False

    @classmethod
    async def check_user_access(cls, user_name: str, service_name: str, func_name: str):
        user_name = user_name if not isinstance(user_name, str) else user_name
        return True if (await cls.get_by(urmusrnm=user_name, urmobjnm='*', urmfncnm='*')) is not None else \
            True if (await cls.get_by(urmusrnm=user_name, urmobjnm='*', urmfncnm=func_name)) is not None else \
                True if (await cls.get_by(urmusrnm=user_name, urmobjnm=service_name, urmfncnm='*')) is not None else \
                    True if (await cls.get_by(urmusrnm=user_name, urmobjnm=service_name,
                                              urmfncnm=func_name)) is not None else \
                        False
