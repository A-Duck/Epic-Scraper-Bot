import DBStuffs

#############################################################################################################

# Checks if the server is password protected, returns false until implemented
def IsServerPasswordProtected():
    ServerPass = DBStuffs.DB_FetchSingle("SERVER_PASSWORD", "Instance")

    if ((ServerPass == "") or (ServerPass == None)):
        return False
    else:
        return True

#############################################################################################################