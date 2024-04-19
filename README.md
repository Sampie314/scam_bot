# ScamBot: Scam Awareness and Prevention Bot

Welcome to ScamBot, a Telegram bot designed to raise scam awareness and help prevent fraudulent activities in Singapore. ScamBot is equipped to offer users guidance on spotting and handling scams, alongside tools for checking the safety of URLs through integration with both URLScan.io and Google Safe Browsing API.

## Features

ScamBot offers the following key features:

- **Generate Scam Newsletter**: Fetches and summarizes the top three latest scam stories in Singapore, providing links to detailed articles and safety tips.
- **Scan a URL**: Analyzes URLs submitted by users to determine their safety status using URLScan.io and Google Safe Browsing API, returning a consolidated safety report.

## How It Works

ScamBot interacts with users via Telegram commands and inline buttons, processing and responding based on the user's selections:

- `/start`: Initiates interaction, presenting the bot's main functionalities.
- `/help`: Provides detailed descriptions of all the features the bot supports.
- Scam newsletter retrieval and URL safety checks are performed as per user requests, with responses dynamically generated based on the latest data from URLScan.io and Google Safe Browsing.

## Getting Started

To get ScamBot up and running, you will need Docker installed on your system. Follow these steps to deploy the bot:

### Prerequisites

1. **Telegram Bot Token**: You need a Telegram bot token, which you can obtain by registering a new bot with BotFather on Telegram.
2. **API Keys**: Ensure you have the necessary API keys for URLScan.io and Google Safe Browsing.

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

    ```bash
    docker run -d scambot
    ```

### File Structure

- bot.py: Main executable script that handles all bot interactions.
- scamscraper.py: Module to fetch scam stories.
- urlscan.py: Interface for URLScan.io API.
- googlescan.py: Interface for Google Safe Browsing API.
- keys.json: Contains API keys and tokens.
- config.json: Contains configuration settings.

### Docker

The Dockerfile provided in the repository sets up the environment needed to run ScamBot. It handles dependencies and ensures that the bot starts automatically upon container startup.
