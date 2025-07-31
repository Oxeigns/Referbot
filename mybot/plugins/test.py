from pyrogram import Client, filters

@Client.on_message(filters.command("ping"))
async def ping_test(_, message):
    await message.reply_text("Pong! (test plugin)")
