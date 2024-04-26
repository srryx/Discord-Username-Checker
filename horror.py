import aiohttp
import asyncio
import json
from os import system
import time
from discord_webhook import DiscordWebhook, DiscordEmbed
import ctypes
import sys

horror = 'Horror V1.1'
system(f'title={horror}')

async def send_to_webhook(status, image_url=""):
    with open("config.json", "r") as f:
        config = json.load(f)
    webhook_url = config["webhook_url"]
    
    webhook = DiscordWebhook(url=webhook_url)
    
    embed = DiscordEmbed()
    embed.title = "horror"
    embed.description = status
    embed.color = 0000
    embed.set_thumbnail(url="https://i.ibb.co/RCNgjvQ/whitecross.png")
    if image_url:
        embed.set_image(url=image_url)
    
    webhook.add_embed(embed)
    
    response = await webhook.execute()

async def check_username(user, proxy_host, proxy_port, proxy_username, proxy_password, speed):
    url = "https://discord.com/api/v9/unique-username/username-attempt-unauthed"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.112 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Referer": "https://discord.com/register",
        "Origin": "https://discord.com"
    }

    proxy = f"http://{proxy_host}:{proxy_port}"
    if proxy_username and proxy_password:
        proxy = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"

    try:
        async with aiohttp.ClientSession() as session:
            data = json.dumps({"username": user.strip()})
            async with session.post(url, headers=headers, data=data, proxy=proxy) as response:
                response_json = await response.json()

                if "taken" in response_json:
                    taken = response_json["taken"]
                    if not taken:
                        status = f"**{user.strip()}** is available."
                        await send_to_webhook(status, image_url="")  
                    else:
                        status = f"**{user.strip()}** is taken."
                    return status
                elif "message" in response_json and response_json["message"] == "The resource is being rate limited.":
                    return "[-] Rate Limited"
                else:
                    return "[-] Error: Something bad went wrong jit"
                    print("Response:", response_json)

                await asyncio.sleep(speed)  # Speed in config
    except Exception as e:
        return f"An error occurred: {str(e)}"

def display_title():
    title = """
    ██   ██  ██████  ██████  ██████   ██████  ██████  
    ██   ██ ██    ██ ██   ██ ██   ██ ██    ██ ██   ██ 
    ███████ ██    ██ ██████  ██████  ██    ██ ██████  
    ██   ██ ██    ██ ██   ██ ██   ██ ██    ██ ██   ██ 
    ██   ██  ██████  ██   ██ ██   ██  ██████  ██   ██                                                                                                                                                                                 
    """
    print(title, end='')

async def start_checking():
    display_title()

    with open("usernames.txt", 'r') as f:
        usernames = f.readlines()

    with open("config.json", "r") as f:
        config = json.load(f)
    proxy_host = config["proxy"]["host"]
    proxy_port = config["proxy"]["port"]
    proxy_username = config["proxy"]["username"]
    proxy_password = config["proxy"]["password"]
    speed = config["speed"]

    max_workers = config.get("max_workers", 10)  # Default is 10 workers if not in config

    print(f"[+] {len(usernames)} usernames loaded")
    print("    [+] Press Enter to start checking", end='')

    input()

    print("    [+] initializing...")

    total_count = len(usernames)
    counter = 0

    tasks = []
    for idx, user in enumerate(usernames, start=1):
        task = asyncio.ensure_future(check_username(user, proxy_host, proxy_port, proxy_username, proxy_password, speed))
        tasks.append(task)

    for result in asyncio.as_completed(tasks):
        status = await result
        counter += 1
        print(f"\r    [+] Checking: {counter}/{total_count} usernames", end='', flush=True)

    print("\n    [+] Checking finished!")

    input("    [+] Press Enter to exit")

if __name__ == "__main__":
    asyncio.run(start_checking())