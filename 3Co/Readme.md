# 3Co
**3Co**(**Co**nnect-**Co**llect-**Co**mpare) is used for health check of the network devices. Mainly, it can be preferable to use pre/post migration and/or integration activities.

 
## What 3Co project does?
**Connect** : It connects to the target device which is defined by user
**Collect** : It collects the outputs of predefined commands
**Compare** : It compares the latest outputs with the previous outputs 


## Why 3Co project is useful?
3Co is useful because it is:
- Vendor Independent(Nokia,Cisco, etc)
- affected, even if a token is used for the connection
- Indepedent from MD-CLI or Classic CLI
- specifying compare type(not equal, smaller than previous output, or in changeable range of the previous output, etc.)


## Requirements 
[Python >= 3.10](https://www.python.org/downloads/)

**Used Libraries** 
- import os, netmiko, configparser, sqlite3, re, smtplib, shutil, pandas
- from getpass import getpass
- from datetime import datetime
- from time import sleep, ctime
- from pytz import timezone, common_timezones
- from subprocess import Popen
- from sys import executable
- from string import Template
- from email.mime.text import MIMEText
- from email.mime.base import MIMEBase
- from email.mime.multipart import MIMEMultipart
- from email import encoders


## How 3Co can be used?
1. Unzip the file
2. Create a *txt* file in *command_db* folder whose name starts with the vendorname.*(__Ex:__ Nokia_HealthCheck.txt)* 
2. Put your command to the created *txt* file
3. Run *doit4me.py* file
4. Follow the guidance of the CLI


## Who maintains and contributes to the project
- Berkay Akar
- Ersin Meşe
- Soner Ersoy


## Where users can get help with your project
If you have any questions, you can send an email to us:

akar.berkay27@gmail.com, ersinmese3@gmail.com, sonerersoy91@gmail.com

