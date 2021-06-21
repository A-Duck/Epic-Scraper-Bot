import Log
import DBStuffs
import json
import os
import sys
import getpass
import subprocess

#############################################################################################################

APP_VERSION = "1.0"

#############################################################################################################

#region Variable Determiners

#############################################################################################################

# Get specified Variable value from OS environment variables
def GetEnvVar(VariableName):
    try:
        Test = os.environ.get(VariableName)
    except:
        Test is None
    return Test

#############################################################################################################

# Get specified Variable value from JSON Settings file
def GetJsonVar(VariableName):
    Test = ""

    try:
        with open('Settings.json', 'r') as Settingsfile:
            SettingsBuffer = Settingsfile.read()

        SettingsArray = json.loads(SettingsBuffer)

        Test = SettingsArray[VariableName]
    except:
        Test is None
    
    return Test

#############################################################################################################

# Gets env, settings file & DB vars then determines & returns the correct value to save
def Get_Variable(VariableName):
    Log.Verbose("Determining {}".format(VariableName))

    ScriptValue = GetJsonVar(VariableName)
    EnvValue = GetEnvVar(VariableName)
    NewValue = ""

    if ((ScriptValue is not None) and (ScriptValue != "")):
        Log.Verbose("Setting Settings file value for {}".format(VariableName))
        NewValue = ScriptValue
    
    if ((EnvValue is not None) and (EnvValue != "")):
        Log.Verbose("Setting environment veriable value for {}".format(VariableName))
        NewValue = EnvValue
    
    return NewValue

#############################################################################################################

#endregion

#############################################################################################################

#region Varible Validity

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

#endregion

#############################################################################################################

# Populate DB vars with values from env / settings file
def PopulateInstanceVars():
    DBStuffs.DB_CreateDatabase()

    DBStuffs.DB_UpdateSettings("TG_Bot_ID", Get_Variable("TG_Bot_ID"))
    DBStuffs.DB_UpdateSettings("SERVER_PASSWORD", Get_Variable("SERVER_PASSWORD"))
    DBStuffs.DB_UpdateSettings("CRON_SCHEDULE", Get_Variable("CRON_SCHEDULE"))
    DBStuffs.DB_UpdateSettings("APP_VERSION", APP_VERSION)

    Evaluate_AllFields()

#############################################################################################################

# Sets up the cron job
def SetUpCronSchedule():
    CurrentDir = os.getcwd()
    Schedule = DBStuffs.DB_FetchSingle("CRON_SCHEDULE", "Instance")
    Username = getpass.getuser()

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
    PopulateInstanceVars()
    SetUpCronSchedule()
    DisplayServerPassword()

    Log.Information("Performing Initial Scrape")
    subprocess.Popen("python Scraper.py", shell = True, stdout=subprocess.PIPE) # First Run of Scraper

    Log.Information("Starting Bot")
    subprocess.run("python EpicScraperV2.py", shell = True, stdout=subprocess.PIPE) # Run Telegram Bot

#############################################################################################################

ControlMethod()
