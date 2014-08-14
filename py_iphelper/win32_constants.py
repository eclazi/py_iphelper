'''
Win32 Constants
'''

win32_errors = [
    'ERROR_BUFFER_OVERFLOW',
    'ERROR_INVALID_DATA',
    'ERROR_INVALID_PARAMETER',
    'ERROR_NO_DATA',
    'ERROR_NOT_SUPPORTED',
    'NO_ERROR'
]

win32_adapter_types = [
    'MIB_IF_TYPE_OTHER',            # Some other type of network interface.
    'MIB_IF_TYPE_ETHERNET',         # An Ethernet network interface.
    'IF_TYPE_ISO88025_TOKENRING',   # MIB_IF_TYPE_TOKENRING
    'MIB_IF_TYPE_PPP',              # A PPP network interface
    'MIB_IF_TYPE_LOOPBACK',         # A software loopback network interface.
    'MIB_IF_TYPE_SLIP',             # An ATM network interface.
    'IF_TYPE_IEEE80211'             # An IEEE 802.11 wireless network interface.
]

all_constants = (
    win32_errors + win32_adapter_types
)