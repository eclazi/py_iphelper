from cffi import FFI

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