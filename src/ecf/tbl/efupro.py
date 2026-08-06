#
# Copyright (c) 2025 Busana Apparel Group. All rights reserved.
#
# This product and it's source code is protected by patents, copyright laws and
# international copyright treaties, as well as other intellectual property
# laws and treaties. The product is licensed, not sold.
#
# The source code and sample programs in this package or parts hereof
# as well as the documentation shall not be copied, modified or redistributed
# without permission, explicit or implied, of the author.
#

__author__ = 'Jaimy Azle'
__version__ = '2.0'
__copyright__ = 'Copyright (c) 2025 Busana Apparel Group'

from artanis.sqlentity import fields
from artanis.sqlentity.sqlorm import Entity


class efupro(Entity):
    """
    User properties
    """
    efususid: str = fields.CharField(max_length=24, label='User ID', unique=True)
    efusmunm: str = fields.CharField(max_length=48, label='User Default Menu Definition')

    @classmethod
    async def get_default_menu(cls, user_name: str) -> str:
        """
        Retrieve default menu name
        :param user_name:
        :return: default menu name
        """
        default_menu: str = "__default_menu__"
        ob = await cls.get(efususid=user_name)
        return default_menu if not ob else default_menu if not ob.efusmunm else ob.efusmunm
