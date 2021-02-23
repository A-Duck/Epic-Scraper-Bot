from datetime import datetime

#############################################################################################################

# Prints a message with a prefix containng the date, time & log level
def Template(Message, Level):
    Message = "{0} - [{1}] - {2}".format(datetime.now(), Level, Message)
    print(Message)

#############################################################################################################

# Calls the Template Method, passes Message & sets Type as "Error"
def Error(Message):
    Template(Message, "Error")

#############################################################################################################

# Calls the Template Method, passes Message & sets Type as "Warning"
def Warning(Message):
    Template(Message, "Warning")

#############################################################################################################

# Calls the Template Method, passes Message & sets Type as "Information"
def Information(Message):
    Template(Message, "Info")

#############################################################################################################

# Calls the Template Method, passes Message & sets Type as "Verbose"
def Verbose(Message):
    Template(Message, "Verbose")

#############################################################################################################