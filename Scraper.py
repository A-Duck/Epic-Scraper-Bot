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
        
        if imgarr["type"] == "OfferImageWide": # Added "OfferImageWide" again because not all games have "DieselStoreFrontWide" (Rogue Legacy - 7 Apr 2022)
            print("Using: OfferImageWide")
            return imgarr["url"]
        elif (imgarr["type"] == "DieselStoreFrontWide"): # Use "DieselStoreFrontWide" because not all games have "OfferImageWide" (2020 December giveaway)
            print("Using: DieselStoreFrontWide")
            return imgarr["url"]
    
    print("Using: Fallback")
    return JsonImageArray[len(imgarr)]["url"] # Added a fallback option in case a game has neither of the above options.
    # The Game should have at least one image that can be used, the fallback option uses the last image in the array because the first may be a vault image (used to hide the next games)

############################################################################################################################

# Returns the date that the game will be free until
def GetPromotionEndDate(JsonPromotionArray):
    for promotion in JsonPromotionArray:
        for subpromotion in promotion["promotionalOffers"]:
                return subpromotion["endDate"][0:10]

############################################################################################################################

# Retrns the page URL for the game
def GetPageURL(element):
    if element["productSlug"] is not None:
        return "https://www.epicgames.com/store/en-US/p/" + element["productSlug"]
    else:
        return "https://www.epicgames.com/store/en-US/p/" + element["catalogNs"]["mappings"][0]["pageSlug"]

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
                    PageURL = GetPageURL(element)
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