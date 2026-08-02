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

from artanis.sqlentity import *

from ecf.core.ecfutils import get_hash_key


class efupro(Entity, table=True):
    """
    User properties
    """
    efususid: str = Field(String(24), label='User ID', primary_key=True)
    efusmunm: str = Field(String(48), label='User Default Menu Definition')
    efusaudt: int = Field(Numeric(8, 0), label='Audit date')
    efusautm: int = Field(Numeric(6, 0), label='Audit time')
    efusauus: str = Field(String(24), label='Audit user')

    @classmethod
    async def get_default_menu(cls, user_name: str) -> str:
        """
        Retrieve default menu name
        :param user_name:
        :return: default menu name
        """
        default_menu: str = "__default_menu__"
        ob = await cls.get(user_name)
        return default_menu if not ob else default_menu if not ob.efusmunm else ob.efusmunm

