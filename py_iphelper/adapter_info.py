from cffi import FFI
import collections

# We have to do all this because time_t isn't defined...??
ffi1 = FFI()
ffi1.cdef("""#define SIZE_OF_TIME_T ...""")
lib = ffi1.verify("""
   #include <sys/types.h>
   #define SIZE_OF_TIME_T  sizeof(time_t)
""")

time_t_type = ''
if lib.SIZE_OF_TIME_T == 4:
    time_t_type = 'int32_t'
elif lib.SIZE_OF_TIME_T == 8:
    time_t_type = 'int64_t'
else:
    raise ValueError('time_t differnt size than expected')

win32_errors = """

#define ERROR_BUFFER_OVERFLOW ...
#define ERROR_INVALID_DATA ...
#define ERROR_INVALID_PARAMETER ...
#define ERROR_NO_DATA ...
#define ERROR_NOT_SUPPORTED ...
#define NO_ERROR ...

"""

structs = """

typedef struct {
  char String[16];
} IP_ADDRESS_STRING, *PIP_ADDRESS_STRING, IP_MASK_STRING, *PIP_MASK_STRING;

typedef struct _IP_ADDR_STRING {
  struct _IP_ADDR_STRING  *Next;
  IP_ADDRESS_STRING      IpAddress;
  IP_MASK_STRING         IpMask;
  DWORD                  Context;
} IP_ADDR_STRING, *PIP_ADDR_STRING;

typedef struct _IP_ADAPTER_INFO {
  struct _IP_ADAPTER_INFO  *Next;
  DWORD                   ComboIndex;
  char                    AdapterName[260];
  char                    Description[132];
  UINT                    AddressLength;
  BYTE                    Address[8];
  DWORD                   Index;
  UINT                    Type;
  UINT                    DhcpEnabled;
  PIP_ADDR_STRING         CurrentIpAddress;
  IP_ADDR_STRING          IpAddressList;
  IP_ADDR_STRING          GatewayList;
  IP_ADDR_STRING          DhcpServer;
  BOOL                    HaveWins;
  IP_ADDR_STRING          PrimaryWinsServer;
  IP_ADDR_STRING          SecondaryWinsServer;
  %(time_t)s              LeaseObtained;
  %(time_t)s              LeaseExpires;
} IP_ADAPTER_INFO, *PIP_ADAPTER_INFO;

""" % {'time_t' : time_t_type }

functions = """

DWORD GetAdaptersInfo( PIP_ADAPTER_INFO pAdapterInfo, PULONG pOutBufLen );

"""

ffi = FFI()
ffi.cdef(win32_errors + structs + functions)

verify = """

#include <winsock2.h>
#include <Iphlpapi.h>

"""

C = ffi.verify(verify, libraries=['IPHLPAPI'])

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