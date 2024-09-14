from ctypes import *

# from definitions.types import *
# from definitions.constants import *
# from definitions.structs.startupInfo import *
# from definitions.structs.processInformation import *
from definitions.my_debugger_defines import *
import os
kernel32 = windll.kernel32

class Debugger():
    def __init__(self):
        pass

    def load(self,path_to_exe):
        if not os.path.exists(path_to_exe):
            print(f"[*] Error: The file {path_to_exe} does not exist.")
            return
        # sets how to create the process in either debug mode or normal mode
        creation_flags = DEBUG_PROCESS # set to CREATE_NEW_CONSOLE if you want to see the process.

        # instantiate the structs
        startupinfo         = STARTUPINFO()
        process_information = PROCESS_INFORMATION()
        startupinfo.dwFlags     = 0x1
        startupinfo.wShowWindow = 0x0

        # We then initialize the cb variable in the STARTUPINFO struct
        # which is just the size of the struct itself
        startupinfo.cb = sizeof(startupinfo)

        if kernel32.CreateProcessA(path_to_exe.encode('utf-8'), # path to the executable
                                   None,
                                   None,
                                   None,
                                   False,
                                   creation_flags,
                                   None,
                                   None,
                                   byref(startupinfo),
                                    byref(process_information)):
            print("[*] We have successfully launched the process!")
            
            print(f"[*] PID: {process_information.dwProcessId}")

        else:
            print("[*] Error: 0x%08x." % kernel32.GetLastError())
            error_code = kernel32.GetLastError()
            error_message = create_string_buffer(256)
            kernel32.FormatMessageA(
                0x00001000,  # FORMAT_MESSAGE_FROM_SYSTEM
                None,
                error_code,
                0,
                error_message,
                len(error_message),
                None
            )
            print(f"[*] Error: 0x{error_code:08x}. {error_message.value.decode()}")



if __name__ == '__main__':
    debugger = Debugger()
    path_to_exe = r"C:\misc\Python-Debugger\sample-executable\CrucialScan.exe"
    # path_to_exe = "./sample-executable/CrucialScan.exe"
    print(path_to_exe)
    debugger.load(path_to_exe)