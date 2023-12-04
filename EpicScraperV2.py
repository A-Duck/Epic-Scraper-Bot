from telegram import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler, ConversationHandler, InlineQueryHandler, MessageHandler, ContextTypes, filters)
from telegram.helpers import escape_markdown
from telegram.constants import ParseMode
import DBStuffs 
import Log
import Common
import Telegram

#############################################################################################################

# Global Variables

# Stages - Used to direct various method callbacks to the next action
state_FirstMenu, state_SilentSend, state_ChangelogSend, state_Password = range(4)

# Callback data - Passed as parameters and used to determine correct method to execute / action to take place
cbd_FALSE, cbd_TRUE, cbd_SETTINGSMENU, cbd_SILENTSEND, cbd_CHANGELOG, cbd_EXIT = range(6)

#############################################################################################################

# Displays the options in within the settings menu
async def Display_SettingsMenu(update, context):
    keyboard = [
        [InlineKeyboardButton("Send Silently", callback_data=str(cbd_SILENTSEND)),
         InlineKeyboardButton("Send Updates", callback_data=str(cbd_CHANGELOG))]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Which Setting would you like to change?",
        reply_markup=reply_markup
    )
    return state_FirstMenu

#############################################################################################################

#region Changelog sending display / set methods

#############################################################################################################

# Display menu for changelog sending
async def Display_Changelog(update, context):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Yes", callback_data=str(cbd_TRUE)),
         InlineKeyboardButton("No", callback_data=str(cbd_FALSE))]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Would you like to receive notifications when updates are available?",
        reply_markup=reply_markup
    )

    return state_ChangelogSend

#############################################################################################################

# enable / disable changelog sending
async def Set_ChangelogSending(update, context):
    query = update.callback_query
    await query.answer()

    NewSetting = update.callback_query.data
    ChatID = str(update.callback_query.message.chat.id)
    
    if (IsChatRegistered(ChatID)):
        if NewSetting == str(cbd_TRUE):
            DBStuffs.DB_Post("UPDATE Telegram SET SendChangelog = \"{}\" WHERE ChatID == {}".format(True, ChatID))
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Update messages enabled")
            Log.Information("Enabled update messages for chat: {}".format(ChatID))
        else:
            DBStuffs.DB_Post("UPDATE Telegram SET SendChangelog = \"{}\" WHERE ChatID == {}".format(False, ChatID))
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Update messages disabled")
            Log.Information("Disabled update messages for chat: {}".format(ChatID))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Chat needs to be registered first")
        Log.Warning("{} tried to set Silent Sending but is not registered".format(ChatID))
        
    return ConversationHandler.END

#############################################################################################################

#endregion

#############################################################################################################

#region SilentSend Display / Set Methods

#############################################################################################################

# Display menu for silent sending
async def Display_SilentSend(update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data=str(cbd_TRUE)),
         InlineKeyboardButton("No", callback_data=str(cbd_FALSE))]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Would you like the messages to be sent without notification?",
        reply_markup=reply_markup
    )

    return state_SilentSend

#############################################################################################################

# enables / disables silent messages
async def Set_SilentSend(update, context):
    query = update.callback_query
    await query.answer()

    NewSetting = update.callback_query.data
    ChatID = str(update.callback_query.message.chat.id)
    
    if (IsChatRegistered(ChatID)):
        if NewSetting == str(cbd_TRUE):
            DBStuffs.DB_Post("UPDATE Telegram SET SendMuted = \"{}\" WHERE ChatID == {}".format(True, ChatID))
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Silent sending enabled")
            Log.Information("Enabled silent sending for chat: {}".format(ChatID))
        else:
            DBStuffs.DB_Post("UPDATE Telegram SET SendMuted = \"{}\" WHERE ChatID == {}".format(False, ChatID))
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Silent sending disabled")
            Log.Information("Disabled silent sending for chat: {}".format(ChatID))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Chat needs to be registered first")
        Log.Warning("{} tried to set Silent Sending but is not registered".format(ChatID))
        
    return ConversationHandler.END

#############################################################################################################

#endregion

#############################################################################################################

#region /Join support methods

#############################################################################################################

# Extract correct Chat name basedo on chat type from the update
def Getchatname(update):
    if (update.message.chat.type == "private"):
        ChatName = update.message.chat.first_name + " " + update.message.chat.last_name
    else:
        ChatName = update.message.chat.title
    
    return ChatName

#############################################################################################################

# Checks if the provided ChatID is in Chat Database, Returns Boolean
def IsChatRegistered(ChatID):
    ChatList = DBStuffs.DB_Fetch("SELECT * FROM Telegram;")
    result = False

    for chat in ChatList:
        if (chat[0] == ChatID):
            result = True
    
    return result

#############################################################################################################

# Saves the chat details to the database, enrolling the chat with the server
async def RegisterChat(update, context):
    ChatName = Getchatname(update)
    ChatID = update.effective_chat.id

    DBStuffs.DB_Post("INSERT INTO Telegram (ChatID, ChatName, SendMuted, SendChangelog) VALUES (\"{}\", \"{}\", \"{}\", \"{}\");".format(ChatID, ChatName, False, False))
    await context.bot.send_message(chat_id=ChatID, text="\"{}\" ({}) is now registered with the server".format(ChatName, ChatID))

    Telegram.SendCurrentGames(ChatID)
    
    Log.Information("\"{}\" ({}) is now registered with the server".format(ChatName, ChatID))

#############################################################################################################

#endregion

#############################################################################################################

# Registers chat with server
async def start(update, context):
    ChatName = Getchatname(update)
    ChatID = str(update.message.chat.id)

    if not IsChatRegistered(ChatID):
        
        if (Common.IsServerPasswordProtected()):
            
            if "/start" in update.message.text:
                await update.message.reply_text("This server is password protected.\nPlease enter the password now or send /cancel to exit")

            context.user_data["IncorrectCount"] = 0
            
            return state_Password
        else:
            RegisterChat(update, context)
            return ConversationHandler.END
            
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="\"{}\" ({}) has already been registered with the server".format(ChatName, ChatID))
        Log.Warning("\"{}\" ({}) has already been registered with the server".format(ChatName, ChatID))
        return ConversationHandler.END

#############################################################################################################

# De-register chat from server
async def stop(update, context):
    ChatID = str(update.message.chat.id)
    ChatName = Getchatname(update)

    if IsChatRegistered(ChatID):
        DBStuffs.DB_Post("DELETE FROM Telegram WHERE ChatID == \"{}\"".format(ChatID))
        await context.bot.send_message(chat_id=update.effective_chat.id, text="\"{}\" ({}) has been de-registered from the server".format(ChatName, ChatID))
        Log.Information("\"{}\" ({}) has been de-registered".format(ChatName, ChatID))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="This chat was never registered")
        Log.Warning("{} tried to de-register {}, but was never registered with the server".format(ChatID, ChatName))
    
    return ConversationHandler.END

#############################################################################################################

# Method to tell user that the command was not recognised
async def UnknownCommand(update, context):
    if ("group" in update.message.chat.type):
        if ("@EpicScraperBot" in update.message.text):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="U WOT M8?")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="U WOT M8?")

    return ConversationHandler.END

#############################################################################################################

# Re-Send the Active games to the current chat
def resend(update, context):
    ChatID = str(update.message.chat.id)
    
    Telegram.SendCurrentGames(ChatID)
    
    return ConversationHandler.END

#############################################################################################################

# returns to the previous menu's handle
async def end(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Exited")
    return ConversationHandler.END

#############################################################################################################

# Verifies that the submitted password matches the server record, Registers chat if successful
async def ValidatePassword(update, context):
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

    SendPass = update.message.text
    ServerPass = DBStuffs.DB_FetchSingle("SERVER_PASSWORD", "Instance")

    context.user_data["IncorrectCount"] += 1

    if context.user_data["IncorrectCount"] <= 3:
        if SendPass == ServerPass:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Password correct. Registering...")
            RegisterChat(update, context)
            return ConversationHandler.END
        else:
            context.bot.edit_message_text("Password Incorrect. (Attempt: {})\nYou can try again, or stop by sending /cancel".format(context.user_data["IncorrectCount"]), chat_id=update.effective_chat.id, message_id=update.message.message_id - context.user_data["IncorrectCount"])
            return state_Password
    else:
        context.bot.edit_message_text("Password Incorrect.\nToo many incorrect attempts. Good Bye", chat_id=update.effective_chat.id, message_id=update.message.message_id - context.user_data["IncorrectCount"])
        Log.Warning("\"{}\" tried to join the server but used an incorrect password 3 times".format(Getchatname(update)))
        return ConversationHandler.END

#############################################################################################################

# Creates listeners for the Telegram bot's menu
def main():
    TG_Bot_ID = DBStuffs.DB_FetchSingle("TG_Bot_ID", "Instance")
    application = Application.builder().token(TG_Bot_ID).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      CommandHandler('settings', Display_SettingsMenu),
                      CommandHandler('resend', resend),
                      CommandHandler('stop', stop),
                      MessageHandler(filters.COMMAND, UnknownCommand)
                    ],
        
        states={
            state_FirstMenu: [CallbackQueryHandler(Display_SilentSend, pattern='^' + str(cbd_SILENTSEND) + '$'),
                              CallbackQueryHandler(Display_Changelog, pattern='^' + str(cbd_CHANGELOG) + '$')],

            state_SilentSend: [CallbackQueryHandler(Set_SilentSend, pattern='^{}|{}$'.format(str(cbd_TRUE), str(cbd_FALSE)))],

            state_ChangelogSend: [CallbackQueryHandler(Set_ChangelogSending, pattern='^{}|{}$'.format(str(cbd_TRUE), str(cbd_FALSE)))],

            state_Password: [MessageHandler(filters.TEXT, ValidatePassword),
                             CommandHandler('cancel', end)]
        },

        fallbacks=[MessageHandler(filters.COMMAND, UnknownCommand)]
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

#############################################################################################################

main()
