set tooldir=C:\ProgramData\Alteryx\Tools

set devpath=%~dp0
if %devpath:~-1%==\ SET devpath=%devpath:~0,-1%
for /f "delims==" %%F in ("%devpath%") do set devfolder=%%~nF
mklink /D "%tooldir%\%devfolder%" "%devpath%"
