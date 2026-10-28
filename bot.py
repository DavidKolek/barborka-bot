import discord
from PIL import Image
import imagehash
from io import BytesIO
from pathlib import Path
import os

TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

target_path = Path(__file__).with_name("target.png")
target_hash = imagehash.phash(
    Image.open(target_path).convert("RGB")
)

@bot.event
async def on_ready():
    print(f"Bot je online: {bot.user}")
    print("Kontrola obrazku je aktivni.")

@bot.event
async def on_message(message):
    if message.author.bot or message.guild is None:
        return

    for attachment in message.attachments:
        if not (attachment.content_type or "").startswith("image/"):
            continue

        try:
            data = await attachment.read()
            image = Image.open(BytesIO(data)).convert("RGB")
            distance = target_hash - imagehash.phash(image)

            if distance <= 4:
                await message.delete()
                print(f"Smazana zprava od {message.author}")

                await message.guild.ban(
                    message.author,
                    reason="Odeslani zakazaneho obrazku"
                )
                print(f"Zabanovan: {message.author}")
                break

        except discord.Forbidden:
            print("Chybi opravneni ke smazani nebo banu.")
        except discord.HTTPException as error:
            print(f"Discord chyba: {error}")
        except Exception as error:
            print(f"Chyba pri kontrole obrazku: {error}")

bot.run(TOKEN)