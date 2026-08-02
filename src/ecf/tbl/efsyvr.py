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


class efsyvr(Entity, table=True):
    """
    System Parameter Param
    """
    efsycono : str = Field(String(3), label='Comp ID', primary_key=True)
    efsyusid : str = Field(String(24), label='User ID', primary_key=True)
    efsypgid : str = Field(String(24), label='Program', primary_key=True)
    efsyvrid : str = Field(String(24), label='Var', primary_key=True)
    efsyvrv0 : str = Field(String(48), label='Value 1')
    efsyvrv1 : str = Field(String(48), label='Value 2')
    efsyvrv2 : str = Field(String(48), label='Value 3')
    efsyvrv3 : str = Field(String(48), label='Value 4')
    efsyvrv4 : str = Field(String(48), label='Value 5')
    efsyvrv5 : str = Field(String(48), label='Value 6')
    efsyvrv6 : str = Field(String(48), label='Value 7')
    efsyvrv7 : str = Field(String(48), label='Value 8')
    efsyvrv8 : str = Field(String(48), label='Value 9')
    efsyvrv9 : str = Field(String(48), label='Value 10')
    efusaudt : int = Field(Numeric(8, 0))
    efusautm : int = Field(Numeric(6, 0))
    efusauus : str = Field(String(24))
