import os
import pyautogui
import base64
from io import BytesIO
from pynput import mouse
from openai import OpenAI

import asyncio
from typing import NoReturn

from telegram import Bot

TOKEN = os.environ.get("TOKEN")
bot = Bot(TOKEN)

async def main(text) -> NoReturn:
    await bot.send_message("", text)


# Initialize OpenAI client
client = OpenAI()

# Function to encode the image from a screenshot
def encode_screenshot():
    screenshot = pyautogui.screenshot()
    buffered = BytesIO()
    screenshot.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# List to store screenshots captured by Button 8
stored_screenshots = []

# Function to handle mouse click for Button 9
def on_click1(x, y, button, pressed):
    if pressed and button == mouse.Button.button9:  # Forward button

        if not stored_screenshots:
            # If no screenshots stored, take one and send it
            base64_image = encode_screenshot()
            response = client.chat.completions.create(
                model="chatgpt-4o-latest",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Help me with what is on the screen."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                        ],
                    }
                ],
            )
            result = response.choices[0].message.content
            loop.run_until_complete(main(result))
            print("==================================================================")
            print(result)
        else:
            # If screenshots are stored, send them
            messages = [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}} for img in stored_screenshots]
            response = client.chat.completions.create(
                model="chatgpt-4o-latest",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Help me with what is on the screen."},
                            *messages,
                        ],
                    }
                ],
            )

            result = response.choices[0].message.content
            print("==================================================================")
            print(result)
            loop.run_until_complete(main(result))

            # Clear stored screenshots after sending
            stored_screenshots.clear()

# Function to handle mouse click for Button 8
def on_click2(x, y, button, pressed):
    if pressed and button == mouse.Button.button8:  # Back button
        base64_image = encode_screenshot()
        stored_screenshots.append(base64_image)

# Listen to mouse events
with mouse.Listener(on_click=lambda x, y, button, pressed: (on_click1(x, y, button, pressed) if button == mouse.Button.button9 else on_click2(x, y, button, pressed))) as listener:
    print("Begin..")
    listener.join()
