import requests
import json
import DBStuffs
import Telegram
import Log

############################################################################################################################

# Gets all information about the games from Epic, returns only the relevant elements
def GetJsonData():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=ZA&allowCountries=ZA"
    headers = {'User-Agent': 'Mozilla/5.0'}

    r = requests.get(url, headers=headers)
    
    JsonData = json.loads(r.text)
    return JsonData["data"]["Catalog"]["searchStore"]["elements"]

############################################################################################################################

# Returns the URL of the correct image from the array of image elements
def GetThumbnail(JsonImageArray):
    for imgarr in JsonImageArray:
        if imgarr["type"] == "DieselStoreFrontWide": # Changed from "OfferImageWide" for 2020 December giveaway
            return imgarr["url"]

############################################################################################################################

# Returns the date that the game will be free until
def GetPromotionEndDate(JsonPromotionArray):
    for promotion in JsonPromotionArray:
        for subpromotion in promotion["promotionalOffers"]:
                return subpromotion["endDate"][0:10]

############################################################################################################################

# Gets information for each game and sends it to the processing method
def FindFreeGames(GamesJson):
    ActiveGames = []

    for element in GamesJson:
        if (element["promotions"] is not None) and (element["price"]["totalPrice"]["discountPrice"] == 0):
            array = element["promotions"]["promotionalOffers"]
            
            try:
                if len(array[0]) != 0:
                    Name = element["title"]
                    ExpiryDate = GetPromotionEndDate(element["promotions"]["promotionalOffers"])
                    PageURL = "https://www.epicgames.com/store/en-US/product/" + element["productSlug"]
                    ImgURL = GetThumbnail(element["keyImages"])
                    
                    ActiveGames.append([Name, ExpiryDate, PageURL, ImgURL])
            except IndexError:
                pass
            
    return ActiveGames

############################################################################################################################

# Adds provided game to the Game table
def SaveNewGamestoDB(Game):
    InsCMD = "INSERT INTO Games(Gamename, Expiry, PageUrl, ImageUrl) VALUES(\"{}\", \"{}\", \"{}\", \"{}\")".format(Game[0], Game[1], Game[2], Game[3])
    DBStuffs.DB_Post(InsCMD)

############################################################################################################################

# Clears previous record of games, notifies about new game and saves it to DB
def ProcessNewGames(NewGamesList):
    DBStuffs.DB_Post("DELETE FROM Games;")
    Log.Information("Previous Games removed from DB")

    for game in NewGamesList:
        SaveNewGamestoDB(game)
        Log.Information("Saved \"{}\" to Database".format(game[0]))
    
    Telegram.SendSameSetToAll(NewGamesList)

############################################################################################################################

# Checks if the games from Epic are different to the DB (previous run)
def CompareGameSets(NewGamesList):
    PreviousGameList = DBStuffs.DB_FetchGameList()

    if PreviousGameList == NewGamesList:
        Log.Information("No New Games Yet :(")
    else:
        Log.Information("New Games are here")
        ProcessNewGames(NewGamesList)

############################################################################################################################

# The main method the application is orchestrated from
def ControlMethod():
    WorkingData = GetJsonData()
    ActiveGameList = FindFreeGames(WorkingData)
    CompareGameSets(ActiveGameList)

############################################################################################################################

ControlMethod()