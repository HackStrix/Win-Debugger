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
        self.pid = None
        self.debugger_active = False
        self.h_thread = None

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

    def open_process(self,pid):

        h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS,False,pid)
        return h_process
    
    def attach(self,pid):

        self.h_process = self.open_process(pid)

        if kernel32.DebugActiveProcess(pid):
            self.debugger_active = True
            self.pid             = int(pid)
            
        else:
            print("[*] Unable to attach to the process.")
            error_code = kernel32.GetLastError()
            print("[*] Error: 0x%08x." % error_code)
            
    def run(self):
        while self.debugger_active == True:
            # check for any debug events
            self.get_debug_event()

    def get_debug_event(self):

        debug_event    = DEBUG_EVENT()
        continue_status= DBG_CONTINUE

        if kernel32.WaitForDebugEvent(byref(debug_event),INFINITE):
            
            # obtain the thread and context information for this event
            print("we got a debug event!")
        
            

            input("Press a key to continue...")
            self.debugger_active = False
            kernel32.ContinueDebugEvent( \
                debug_event.dwProcessId, \
                debug_event.dwThreadId, \
                continue_status )
            
    def detach(self):
       if kernel32.DebugActiveProcessStop(self.pid):
            print("[*] Finished debugging. Exiting...")
            return True
       else:
            print("[*] There was an error")
            error_code = kernel32.GetLastError()
            print("[*] Error: 0x%08x." % error_code)
            return False

        
    def open_thread(self, thread_id):

        h_thread = kernel32.OpenThread(THREAD_GET_CONTEXT | THREAD_SUSPEND_RESUME, None,
            thread_id)

        if h_thread is not None:
                return h_thread
        else:
            print ("[*] Could not obtain a valid thread handle.")
            return False

    def enumerate_threads(self):

            thread_entry = THREADENTRY32()
            thread_list  = []
            snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, self.pid)

            if snapshot is not None:
                # You have to set the size of the struct
                # or the call will fail
                thread_entry.dwSize = sizeof(thread_entry)
                success = kernel32.Thread32First(snapshot,
                byref(thread_entry))

                while success:
                    if thread_entry.th32OwnerProcessID == self.pid:
                        thread_list.append(thread_entry.th32ThreadID)
                    success = kernel32.Thread32Next(snapshot,
                    byref(thread_entry))

                kernel32.CloseHandle(snapshot)
                return thread_list
            else:
                return False

    def get_thread_context (self, thread_id=None,h_thread=None):

        context = WOW64_CONTEXT()
        context.ContextFlags = CONTEXT_FULL | CONTEXT_DEBUG_REGISTERS

        # Obtain a handle to the thread
        if h_thread is None:
            h_thread = self.open_thread(thread_id)
            print(h_thread)
        if h_thread and kernel32.Wow64SuspendThread(h_thread) != -1:
            # Get the context
            context_status = kernel32.Wow64GetThreadContext(h_thread, byref(context))
            print(context_status)
            if context_status != 0:
                # print(context.Eip)
                kernel32.ResumeThread(h_thread)
                return context
            else:
                print("[*] GetThreadContext failed.")
                kernel32.ResumeThread(h_thread)
                print(kernel32.GetLastError())
                return False
        else:
            print("[*] Could not obtain a valid thread handle. or could not suspend the thread")
            return False
       
if __name__ == '__main__':
    # debugger = Debugger()
    # path_to_exe = r"C:\misc\Python-Debugger\sample-executable\CrucialScan.exe"
    # # path_to_exe = "./sample-executable/CrucialScan.exe"
    # print(path_to_exe)
    # debugger.load(path_to_exe)

    debugger = Debugger()

    pid = input("Enter the PID of the process to attach to: ")
    debugger.attach(int(pid))
    # debugger.run()
    list1 = debugger.enumerate_threads()
    print(list1)
# For each thread in the list we want to
# grab the value of each of the registers
    for thread in list1:

        thread_context = debugger.get_thread_context(thread)
        if thread_context:
            # Now let's output the contents of some of the registers
            print("[*] Dumping registers for thread ID: 0x%08x" % thread)
            print("[**] EIP: 0x%08x" % thread_context.Eip)
            print("[**] ESP: 0x%08x" % thread_context.Esp)
            print("[**] EBP: 0x%08x" % thread_context.Ebp)
            print("[**] EAX: 0x%08x" % thread_context.Eax)
            print("[**] EBX: 0x%08x" % thread_context.Ebx)
            print("[**] ECX: 0x%08x" % thread_context.Ecx)
            print("[**] EDX: 0x%08x" % thread_context.Edx)
            print("[*] END DUMP")
            
debugger.detach()
