# ScamBot: Scam Awareness and Prevention Bot

Welcome to ScamBot, a Telegram bot designed to raise scam awareness and help prevent fraudulent activities in Singapore. ScamBot is equipped to offer users guidance on spotting and handling scams, alongside tools for checking the safety of URLs through integration with both URLScan.io and Google Safe Browsing API.

## How It Works

ScamBot interacts with users via Telegram commands and inline buttons, processing and responding based on the user's selections:

- `/start`: Initiates interaction, presenting the bot's main functionalities.
- `/help`: Provides detailed descriptions of all the features the bot supports.

### Features

The following are the key features offered by ScamBot that are available for user selection:

- **Generate Scam Newsletter**: Fetches and summarizes the top three latest scam stories in Singapore, providing links to detailed articles and safety tips.
- **Scan a URL**: Analyzes URLs submitted by users to determine their safety status using URLScan.io and Google Safe Browsing API, returning a consolidated safety report.
- **Check Scam Message**: Users can submit messages to check if they could potentially be scam messages. The function evaluates the message, returns whether it is likely a scam, and provides the number of users who have previously submitted the same message along with advice for further actions.
- **I've Been Scammed!**: Offers immediate assistance and information to users who have been scammed. It provides steps on what to do next, such as contacting banks, filing police reports, and seeking emotional support.

## Getting Started

To get ScamBot up and running, you will need Docker installed on your system. Follow these steps to deploy the bot:

### Prerequisites

1. **Telegram Bot Token**: You need a Telegram bot token, which you can obtain by registering a new bot with BotFather on Telegram.
2. **API Keys**: Ensure you have the necessary API keys for URLScan.io, Google Safe Browsing, and openAI.

### Setup Instructions

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/your-github/scambot.git
    cd scambot
    ```

2. **Configuration**:
    - Place your Telegram bot token and other API keys in the keys.json file.
    - Adjust any configuration settings in config.json.

3. **Build and Run with Docker:**
    - Ensure Docker is running on your machine.
    - Build the Docker image:

    ```bash
    docker build -t scambot .
    ```

    - Run the Docker container:
    - 
    ```bash
    docker run -d --name scambot scambot 
    ```
   
    - if running on EC2:
    ```bash
    docker run --name redis-host --network app-network -p 6379:6379 -d redis
    docker run --name scambot --network app-network -d scambot
    ```

### File Structure

- bot.py: Main executable script that handles all bot interactions.
- agenttools.py: Includes tools for the LangChain API to extend bot functionality.
- scamscraper.py: Module to fetch scam stories for the scam newsletter creation.
- urlscan.py: Manages communication with the urlscan.io API for checking URLs.
- googlescan.py: Manages communication with the Google Safe Browsing API for checking URLs.
- checkscam.py: Manages scam message checks and integrates with Redis to track message occurrence.
- keys.json: Contains API keys and tokens.
- config.json: Contains configuration settings.
- requirements.txt: Lists all dependencies required to run the bot.

### Docker

The Dockerfile provided in the repository sets up the environment needed to run ScamBot. It handles dependencies and ensures that the bot starts automatically upon container startup.
