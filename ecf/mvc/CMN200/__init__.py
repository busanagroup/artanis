__author__ = 'jaimy'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2009 My Company'

from ecf.core.mvcsvc import *
from ecf.tbl import csyinf


class CMN200(MVCController):
    """
    Business Partner Manager
    """

    _description = 'Business Partner.Open'
    _supported_functions = (MVCFuncNew, MVCFuncOpen, MVCFuncShow, MVCFuncCopy, MVCFuncDelete)
    _model_binder = MVCModelBinder(csyinf)

    cridcono = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, String(3), label='Company No.', charcase=ecUpperCase,
                        enable=False, visible=False)
    crididcd = MVCField(MVCTypeList + MVCTypeField, String(8), label='Code ', charcase=ecUpperCase)
    crididnm = MVCField(MVCTypeList + MVCTypeField, String(24), label='Name', synchronized=True)
    crididds = MVCField(MVCTypeField + MVCTypeList, String(48), label='Description')
    cridtype = MVCField(MVCTypeField + MVCTypeParam, Integer, label='Type')
    cridgrcd = MVCField(MVCTypeField + MVCTypeParam, String(4), label='Group', synchronized=True, browseable=True,
                        charcase=ecUpperCase)
    cridgrnm = MVCField(MVCTypeField, String(24), label='Group', enabled=False)
    cridpcnm = MVCField(MVCTypeList + MVCTypeField, String(24), label='PIC')
    cridadr1 = MVCField(MVCTypeField, String(48), label='Address1')
    cridadr2 = MVCField(MVCTypeField, String(48), label='Address2')
    cridadr3 = MVCField(MVCTypeField, String(48), label='Address3')
    cridarid = MVCField(MVCTypeField, String(3), label='City ', charcase=ecUpperCase, synchronized=True,
                        browseable=True)
    cridarnm = MVCField(MVCTypeField, String(48), label='City', enabled=False)
    cridstid = MVCField(MVCTypeField, String(3), label='Provincy ', charcase=ecUpperCase, synchronized=True,
                        browseable=True)
    cridstnm = MVCField(MVCTypeField, String(48), label='Provincy', enabled=False)
    cridctid = MVCField(MVCTypeField, String(3), label='Country ', charcase=ecUpperCase, synchronized=True,
                        browseable=True)
    cridctnm = MVCField(MVCTypeList + MVCTypeField, String(48), label='Country', enabled=False)
    cridzipc = MVCField(MVCTypeField, String(48), label='Zip')
    cridphn1 = MVCField(MVCTypeField, String(24), label='Phone1')
    cridphn2 = MVCField(MVCTypeField, String(24), label='Phone2')
    cridfax1 = MVCField(MVCTypeField, String(24), label='Fax1')
    cridfax2 = MVCField(MVCTypeField, String(24), label='Fax2')
    cridnpwp = MVCField(MVCTypeField + MVCTypeList, String(24), label='NPWP', charcase=ecUpperCase)
    cridstat = MVCField(MVCTypeList + MVCTypeField + MVCTypeParam, Integer, label='Active Status',
                        choices={'Active': 1, 'Inactive': 0})

    async def hello(self):
        return await self.get_program_redirection('100', '200', '300')