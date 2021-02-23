import requests
import DBStuffs

############################################################################################################################

# Fetch Telegram bot ID from DB and save to variable for faster access
def TGInitialise():
    TGBotID = DBStuffs.DB_FetchSingle("TG_Bot_ID", "Instance")
    
    if TGBotID[0:3] != "bot":
        TGBotID = "bot" + TGBotID

    return TGBotID

############################################################################################################################

# Sends Telegram Message
def SendSingle(Name, ExpiryDate, PageURL, ImgURL, ChatID, SilentSend):
    TGBotID = TGInitialise()

    TelegramSendURL = "https://api.telegram.org/" + TGBotID + "/sendPhoto"
    
    # Fail safe for Epic banner not being found

    Caption = """*New Free Game*\n\n*Name:* {}\n*Free Until:* {}\n\n{}""".format(Name, ExpiryDate, PageURL)
    Payload = {'chat_id': ChatID, 'photo': ImgURL, 'parse_mode': 'Markdown', 'caption': Caption, 'disable_notification': SilentSend}
    requests.post(TelegramSendURL, data = Payload)

############################################################################################################################

# Send Game Set to specific ChatID
def SendGameSet(games, ChatID, SilentSend):
    for game in games:
        SendSingle(game[0], game[1], game[2], game[3], ChatID, SilentSend)

############################################################################################################################

# Send game set to each registered chat in DB
def SendSameSetToAll(games):
    ChatList = DBStuffs.DB_Fetch("SELECT ChatID, SendMuted FROM Telegram;")

    for Chat in ChatList:
        SendGameSet(games, Chat[0], Chat[1])

############################################################################################################################

# Send the Active games to the Specified chat
def SendCurrentGames(ChatID):
    SilentSendEnabled = DBStuffs.DB_GetSilentSend(ChatID)

    GameList = DBStuffs.DB_FetchGameList()
    SendGameSet(GameList, ChatID, SilentSendEnabled)

############################################################################################################################