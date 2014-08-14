from _cffi import *

import collections

def is_error(err):
    return err != C.NO_ERROR

def _c_GetAdaptersInfo():
    adapters = ffi.new('IP_ADAPTER_INFO[1]')
    ptr_size = ffi.new('PULONG', ffi.sizeof(adapters))

    # Get required size of array
    err = C.GetAdaptersInfo(adapters, ptr_size)
    if is_error(err):
        if err != C.ERROR_BUFFER_OVERFLOW:
            raise WindowsError(ffi.getwinerror(err))

    adapters = ffi.cast('PIP_ADAPTER_INFO', ffi.new('char[%d]' % ptr_size[0]))
    err = C.GetAdaptersInfo(adapters, ptr_size)
    if is_error(err):
        raise WindowsError(ffi.getwinerror(err))

    return adapters

IpAddress_fields = [
    'IpAddress',
    'IpMask',
    'Context'
]

IpAddress = collections.namedtuple('IpAddr', IpAddress_fields)

AdapterInfo_fields = [
        'ComboIndex',
        'AdapterName',
        'Description',
        'Address',
        'Index',
        'Type',
        'DhcpEnabled',
        'IpAddressList',
        'GatewayList',
        'DhcpServer',
        'HaveWins',
        'PrimaryWinsServer',
        'SecondaryWinsServer',
        'LeaseObtained',
        'LeaseExpires'
        ]

AdapterInfo = collections.namedtuple(
    'AdapterInfo',
    AdapterInfo_fields
)

def mac_address_to_string(address, length):
    return ''.join(['{:X}'.format(address[i]) for i in range(length)])

def create_IpAddress(c_ip_addr):
    return IpAddress(
        ffi.string(c_ip_addr.IpAddress.String),
        ffi.string(c_ip_addr.IpMask.String),
        c_ip_addr.Context
    )

def ip_address_list_to_list(c_ip_addr):
    addrs = []
    while c_ip_addr:
        addrs.append(create_IpAddress(c_ip_addr))
        if(c_ip_addr.Next):
            c_ip_addr = c_ip_addr.Next[0]
        else:
            break
    return addrs

def create_AdapterInfo(c_adapter):
    return AdapterInfo(
            c_adapter.ComboIndex,
            ffi.string(c_adapter.AdapterName),
            ffi.string(c_adapter.Description),
            mac_address_to_string(c_adapter.Address, c_adapter.AddressLength),
            c_adapter.Index,
            c_adapter.Type,
            bool(c_adapter.DhcpEnabled),
            ip_address_list_to_list(c_adapter.IpAddressList),
            ip_address_list_to_list(c_adapter.GatewayList),
            ip_address_list_to_list(c_adapter.DhcpServer),
            bool(c_adapter.HaveWins),
            ip_address_list_to_list(c_adapter.PrimaryWinsServer),
            ip_address_list_to_list(c_adapter.SecondaryWinsServer),
            c_adapter.LeaseObtained,
            c_adapter.LeaseExpires
    )

def GetAdaptersInfo():
    adapters = []
    c_adapters = _c_GetAdaptersInfo()
    while (c_adapters):
        c_adapter = c_adapters[0]
        adapters.append(create_AdapterInfo(c_adapter))
        c_adapters = c_adapter.Next
    return adapters