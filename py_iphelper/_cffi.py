from cffi import FFI
from win32_constants import all_constants

def get_time_t_type():
    # We need to figure out the typedef of time_t for the current platform
    ffi_time_t = FFI()
    ffi_time_t.cdef('''#define SIZE_OF_TIME_T ...''')
    time_t_lib = ffi_time_t.verify('''
       #include <sys/types.h>
       #define SIZE_OF_TIME_T  sizeof(time_t)
    ''')
    if time_t_lib.SIZE_OF_TIME_T == 4:
        return 'int32_t'
    elif time_t_lib.SIZE_OF_TIME_T == 8:
        return 'int64_t'
    else:
        raise ValueError('time_t different size than expected')

_time_t_type = get_time_t_type()

def _make_defines():
    return '\n'.join(['#define %s ...' % constant for constant in all_constants])

win32_defines = _make_defines()

win32_structs = \
'''
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
''' \
% {'time_t' : _time_t_type }

win32_functions = \
'''
DWORD GetAdaptersInfo( PIP_ADAPTER_INFO pAdapterInfo, PULONG pOutBufLen );
'''

def _make_includes(includes):
    return '\n'.join(['#include <%s>' % include for include in includes])

win32_cdef = '\n'.join([win32_defines, win32_structs, win32_functions])

ffi = FFI()
ffi.cdef(win32_cdef)

win32_include_files = [
    'winsock2.h',
    'Iphlpapi.h'
]

win32_includes = _make_includes(win32_include_files)

win32_libs = [
    'IPHLPAPI'
]

C = ffi.verify(win32_includes, libraries=win32_libs)