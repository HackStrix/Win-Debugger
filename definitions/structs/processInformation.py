from ctypes import *
from definitions.types import *
from definitions.constants import *

class PROCESS_INFORMATION(Structure):
    _fields_ = [
    ("hProcess", HANDLE ),
    ("hThread", HANDLE ),
    ("dwProcessId", DWORD ),
    ("dwThreadId", DWORD )
    ]