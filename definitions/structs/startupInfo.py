from ctypes import *
from definitions.types import *
from definitions.constants import *


class STARTUPINFO(Structure):
    _fields_ = [
    ("cb", DWORD ),
    ("lpReserved", LPTSTR ),
    ("lpDesktop", LPTSTR ),
    ("lpTitle", LPTSTR ),
    ("dwX", DWORD ),
    ("dwY", DWORD ),
    ("dwXSize", DWORD ),
    ("dwYSize", DWORD ),
    ("dwXCountChars", DWORD ),
    ("dwYCountChars", DWORD ),
    ("dwFillAttribute", DWORD ),
    ("dwFlags", DWORD ),
    ("wShowWindow", WORD ),
    ("cbReserved2", WORD ),
    ("lpReserved2", LPBYTE ),
    ("hStdInput", HANDLE ),
    ("hStdOutput", HANDLE ),
    ("hStdError", HANDLE ),
    ]