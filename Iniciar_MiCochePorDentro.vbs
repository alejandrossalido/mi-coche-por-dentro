Set Shell = CreateObject("WScript.Shell")
Set Fso = CreateObject("Scripting.FileSystemObject")
BaseDir = Fso.GetParentFolderName(WScript.ScriptFullName)
PythonW = Fso.BuildPath(BaseDir, ".venv\Scripts\pythonw.exe")
Launcher = Fso.BuildPath(BaseDir, "desktop_launcher.py")
Shell.CurrentDirectory = BaseDir
Shell.Run """" & PythonW & """ """ & Launcher & """", 0, False
