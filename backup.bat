@echo off
set DATUM=%date:~-4%-%date:~3,2%-%date:~0,2%
copy "C:\Projekti\NasiProjekti\instance\projekti.db" "\\Zabok-DC\JavniDisk\ProjektiBackup\projekti_%DATUM%.db"