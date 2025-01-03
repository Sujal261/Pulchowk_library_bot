import disnake
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time
import asyncio
import os
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()
keep_alive()
# Discord Client Setup
intents = disnake.Intents.default()
intents.message_content = True  # This is the privileged intent we need
intents.members = False  # Disable member intent since we don't need it
intents.presences = False  # Disable presence intent since we don't need it
client = disnake.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!"):
        try:
            # Get the username from the message
            username = message.content[
                1:
            ].strip()  # Remove the "!" and any surrounding spaces
            if not username:
                await message.channel.send("Please provide your username after '!'.")
                return

            password = username  # Use the same value for both username and password
            await message.channel.send("Starting the data retrieval process...")
            await selenium_task(message, username, password)
        except Exception as e:
            await message.channel.send(f"An error occurred: {str(e)}")


async def selenium_task(message, username, password):
    def run_selenium():
        # Set up Chrome WebDriver with options
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--disable-dev-shm-usage")  # Disable shared memory usage
        options.add_argument("--no-sandbox")  # Disable sandbox for Docker
        options.add_argument("--disable-gpu")  # Disable GPU acceleration
        options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging

        # Explicitly set Chrome binary path
        options.binary_location = "/usr/bin/google-chrome"

        # Use webdriver_manager to install and manage ChromeDriver
        chromedriver_path = ChromeDriverManager().install()
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)

        try:
            # Open the website
            driver.get("http://pulchowk.elibrary.edu.np/")

            # Click the "Sign In" button
            signin_button = driver.find_element(
                By.XPATH, "//span[contains(text(), 'Sign In')]"
            )
            signin_button.click()

            # Enter username and password
            driver.find_element(By.ID, "Username").send_keys(username)
            driver.find_element(By.ID, "Password").send_keys(password)

            # Submit login form
            driver.find_element(By.ID, "btnSubmit").click()

            roll_number_element = driver.find_element(
                By.XPATH, f"//span[contains(text(), '{username}')]"
            )
            roll_number_element.click()


            profile_link = driver.find_element(By.ID, "userProfile")
            profile_link.click()

            table = driver.find_element(By.CLASS_NAME, "table-striped")
            rows = table.find_elements(By.TAG_NAME, "tr")

            table_data = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                row_data = [cell.text for cell in cells[:-1]]
                if row_data:
                    table_data.append(row_data)

            return table_data

        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            driver.quit()

    try:
        table_data = await client.loop.run_in_executor(None, run_selenium)

        if isinstance(table_data, str) and table_data.startswith("Error"):
            await message.channel.send(table_data)
            return

        if table_data:
            response = "Books you took\n"
            for row in table_data:
                response += f"{' | '.join(row)}\n"

            if len(response) > 1900:
                parts = [response[i : i + 1900] for i in range(0, len(response), 1900)]
                for part in parts:
                    await message.channel.send(f"```{part}```")
            else:
                await message.channel.send(f"```{response}```")
        else:
            await message.channel.send("No data found in the table.")

    except Exception as e:
        await message.channel.send(
            f"An error occurred while processing the data: {str(e)}"
        )

token = os.getenv("BOT_TOKEN")
client.run(token)
