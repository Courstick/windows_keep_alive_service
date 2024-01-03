import socket
import json
import time
import psutil
import os
import sys
import subprocess

import win32serviceutil
import win32service
import win32event
import servicemanager


class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "KeepAliveService"
    _svc_display_name_ = "Keep Alive Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        try:
            self.main()
        except Exception as e:
            servicemanager.LogErrorMsg(f"Service failed to start: {str(e)}")
            raise

    def main(self):
        while True:
            for proc in psutil.process_iter(['pid', 'environ', 'cmdline', 'name']):
                try:
                    if proc.name() == "python.exe" and proc.status() == 'running' and "process_name" in proc.cmdline():
                        break
                except psutil.AccessDenied:
                    pass
            else:
                self.start_process()
            time.sleep(5)

    @staticmethod
    def start_process():
        command = 'start xxx.exe'
        subprocess.Popen(command, shell=True)


if __name__ == '__main__':
    # could packaged by pyinstaller
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppServerSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AppServerSvc)
