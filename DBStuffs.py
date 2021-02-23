import sqlite3
import Log

############################################################################################################################

DBFILENAME = "scraper.db"

############################################################################################################################

# Creates DB is not already there, populates structure if not already there
def DB_CreateDatabase():
    conn = sqlite3.connect(DBFILENAME)
    cursor = conn.cursor()
    
    sqlfile = open("InitDB.sql", "r")
    cursor.executescript(sqlfile.read())

    if DB_GetRowCount("Instance") == 0:
        DB_Post("INSERT INTO Instance VALUES ('', '', '', '');")

    conn.close()

############################################################################################################################

# Generic Execution method for return queries (eg: Select)
def DB_Fetch(SQLCommand):
    ResultSet = []

    conn = sqlite3.connect(DBFILENAME)
    cursor = conn.cursor()
	
    for row in cursor.execute(SQLCommand):
        RowRecord = []
        
        for column in row:
            RowRecord.append(column)
        
        ResultSet.append(RowRecord)

    conn.close()

    return ResultSet

############################################################################################################################

# Generic Execution method for return queries (eg: Select)
def DB_FetchSingle(Field, Table):
    Result = ""

    conn = sqlite3.connect(DBFILENAME)
    cursor = conn.cursor()
	
    for row in cursor.execute("SELECT {} FROM {}".format(Field, Table)):        
        Result = row[0]

    conn.close()

    return Result

############################################################################################################################

# Generic Execution method for non return queries (eg: Insert, Update, Delete)
def DB_Post(SQLCommand):
    conn = sqlite3.connect(DBFILENAME)
			
    conn.execute(SQLCommand)
    conn.commit()

    conn.close()

############################################################################################################################

# Updates the specified field with specified value if a differrence exists
def DB_UpdateSettings(Field, NewValue):
    CurrentValue = DB_FetchSingle(Field, "Instance")

    if ((CurrentValue != NewValue) and (NewValue != "")):
        DB_Post("UPDATE Instance SET {} = '{}';".format(Field, NewValue))

    Log.Information("{} saved to DB".format(Field))

############################################################################################################################

# Returns a count of rows in a specified table
def DB_GetRowCount(Table):
    conn = sqlite3.connect(DBFILENAME)
    cursor = conn.cursor()
    Results = 0
	
    for row in cursor.execute("SELECT * FROM {}".format(Table)):
        Results += 1

    conn.close()

    return Results

############################################################################################################################

# Returns a list of games in the database 
def DB_FetchGameList():
    GameList = DB_Fetch("SELECT GameName, Expiry, PageUrl, ImageUrl FROM Games")
    return GameList

############################################################################################################################

# Returns a list of games in the database 
def DB_GetSilentSend(ChatID):
    Result = False

    conn = sqlite3.connect(DBFILENAME)
    cursor = conn.cursor()
	
    for row in cursor.execute("SELECT SendMuted FROM Telegram WHERE ChatID = {}".format(ChatID)):        
        Result = row[0]

    conn.close()

    return Result

############################################################################################################################