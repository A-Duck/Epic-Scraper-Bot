from dotenv import load_dotenv
import Log
import DBStuffs
import json
import os
import sys
import getpass
import subprocess

#############################################################################################################

# Gets env, settings file & DB vars then determines & returns the correct value to save
def Get_Variable(VariableName):
    Log.Verbose("Determining {}".format(VariableName))
    
    return os.getenv(VariableName)

#############################################################################################################

# Checks if mandatory fields have been provided, Exits with appropriate message if not
def Evaluate_Validity(Field):
    if DBStuffs.DB_FetchSingle(Field, "Instance") == "":
        print("{} not specified, exiting...".format(Field))
        sys.exit(0)

#############################################################################################################

# Evaluates Validity for each mandatory variable
def Evaluate_AllFields():
    Evaluate_Validity("TG_Bot_ID")
    Evaluate_Validity("CRON_SCHEDULE")

#############################################################################################################

# Populate DB vars with values from env / settings file
def PopulateInstanceVars():
    DBStuffs.DB_CreateDatabase()

    DBStuffs.DB_UpdateSettings("TG_Bot_ID", Get_Variable("TG_Bot_ID"))
    DBStuffs.DB_UpdateSettings("SERVER_PASSWORD", Get_Variable("SERVER_PASSWORD"))
    DBStuffs.DB_UpdateSettings("CRON_SCHEDULE", Get_Variable("CRON_SCHEDULE"))

    Evaluate_AllFields()

#############################################################################################################

# Sets up the cron job
def SetUpCronSchedule():
    CurrentDir = os.getcwd()
    Schedule = DBStuffs.DB_FetchSingle("CRON_SCHEDULE", "Instance")

    Log.Verbose("Directory: {}/Scraper.py".format(CurrentDir))
    Log.Verbose("Schedule: {}".format(Schedule))

    os.system('echo "{0} root cd /app && /usr/local/bin/python {1}/Scraper.py >> /dev/stdout\n" >> /etc/cron.d/EpicScraper'.format(Schedule, CurrentDir))
    os.system('chmod 644 /etc/cron.d/EpicScraper')
    os.system('/etc/init.d/cron reload')
    os.system('service cron restart')

    Log.Information("Cron schedule set")

#############################################################################################################

# Displays a server password if the password is enabled
def DisplayServerPassword():
    TopSecret = DBStuffs.DB_FetchSingle("SERVER_PASSWORD", "Instance")

    if TopSecret != "":
        Output = ""
        Output += "\n"
        Output += "##################################\n"
        Output += "### Server Password:\n"
        Output += "### {}\n".format(TopSecret)
        Output += "##################################"
        Output += "\n"

        print(Output)

#############################################################################################################

# Orchestrator method
def ControlMethod():
    load_dotenv()
    PopulateInstanceVars()
    SetUpCronSchedule()
    DisplayServerPassword()

    Log.Information("Performing Initial Scrape")
    subprocess.Popen("python Scraper.py", shell = True, stdout=subprocess.PIPE) # First Run of Scraper

    Log.Information("Starting Bot")
    subprocess.run("python EpicScraperV2.py", shell = True, stdout=subprocess.PIPE) # Run Telegram Bot

#############################################################################################################

ControlMethod()