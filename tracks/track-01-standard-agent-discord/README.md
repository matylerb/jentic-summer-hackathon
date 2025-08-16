# Discord Agent Bot with Groq and Jentic

This is an advanced Discord bot that uses the Groq API for powerful language processing and the Jentic platform to interact with external tools. The bot features a modern slash command interface, remembers conversation context, and provides rich, embedded responses.

## ✨ Features

- **Modern Discord UX**: Uses slash commands (`/wiki`, `/help`, `/reset`, `/chess` ) instead of old-style prefixes.
- **AI-Powered Agent**: Leverages the speed of the Groq API (running Llama 3) to understand and respond to user queries.
- **Tool Integration**: Connects to the Jentic platform to discover and execute tools, allowing the agent to perform actions.
- **Conversation Context**: Remembers the history of your conversation, allowing for natural follow-up questions.
- **Rich Embed Responses**: Formats replies in clean, easy-to-read Discord embeds.
- **Progress Indicators**: Shows a "Bot is thinking..." message for long-running tasks.
- **Fun Games**: Blackjack and Chess, test your luck and mind! 
- **Owner-Only Sync Command**: A secure `!sync` command for instantly updating slash commands during development.

---

## 🚀 Setup Instructions

Follow these steps to get the bot running in your own server.

### 1. Prerequisites

- Python 3.8 or higher.
- A Discord account and a server where you have administrator permissions.
- API keys from Discord, Groq, and Jentic.

### 2. Create a Discord Application

1.  Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2.  Click **"New Application"** and give it a name.
3.  Go to the **"Bot"** tab, click **"Reset Token"**, and copy your bot token. **This is your `DISCORD_TOKEN`**.

### 3. Get API Keys

- **Groq**: Go to the [Groq Console](https://console.groq.com/keys) to get your **`GROQ_API_KEY`**.
- **Jentic**: Go to your Jentic dashboard to get your **`JENTIC_AGENT_API_KEY1`**.

### 4. Project Setup

1.  **Clone the Repository (or download the code)**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-folder>
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv .venv
    # On Windows
    .\.venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    Create a file named `requirements.txt` with the following content:
    ```
    discord.py
    python-dotenv
    groq
    jentic
    ```
    Then, run the installation command:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a file named `.env` in your project's main folder and add your secret keys:
    ```env
    DISCORD_TOKEN="your_discord_bot_token_here"
    GROQ_API_KEY="your_groq_api_key_here"
    JENTIC_AGENT_API_KEY1="your_jentic_api_key_here"
    ```

### 5. Invite the Bot to Your Server

1.  Go back to the **Discord Developer Portal** -> Your Application.
2.  Go to **"OAuth2"** -> **"URL Generator"**.
3.  In the "Scopes" section, tick both **`bot`** and **`applications.commands`**.
4.  In the "Bot Permissions" section that appears, select **"Send Messages"** and **"Read Message History"**.
5.  Copy the generated URL, paste it into your browser, and invite the bot to your server.

### 6. Run the Bot

1.  Make sure your virtual environment is active.
2.  Run the main Python script from your terminal:
    ```bash
    python main.py
    ```
    You should see a "We have logged in as..." message.

### 7. Sync Slash Commands

1.  In any channel in your Discord server, type the message `!sync`.
2.  The bot will confirm that the slash commands have been synced. They should now be available to use.

---

## 📖 Usage Examples

### `/agent`
Ask the agent to perform a task. It will use its tools if necessary.

> **You:** `/agent query: send a welcome message to the general channel`
>
> **Bot:** (Thinking...)
>
> **Bot:** (Calls the `discord_send_message` tool)
>
> **Bot:** (Embed) **Query:** send a welcome message to the general channel
> I have sent the welcome message to the #general channel as you requested.

### `/help`
Displays a list of available commands.

> **You:** `/help`
>
> **Bot:** (Embed) **Bot Help**
> - **/agent `query`**: Ask the agent to perform a task...
> - **/reset**: Clears your personal conversation history...
> - **/help**: Shows this help message.

---

## ⚙️ Supported Capabilities

- **AI Model**: Groq (llama3-70b-8192)
- **Tool Platform**: Jentic
- **Available Tools**:
    - **Discord**: The agent can use tools to interact with Discord (e.g., send messages, create channels), provided they are available on your Jentic account.

---

## 🔧 Troubleshooting Guide

- **Slash Commands Not Appearing**:
    1.  Make sure you re-invited the bot with both the `bot` and `applications.commands` scopes (Step 5).
    2.  Run the `!sync` command in your server.
    3.  If they still don't appear, fully restart your Discord client (Ctrl+R on the desktop app).

- **"Invalid or inactive API key" Error**:
    1.  Double-check that the keys in your `.env` file are correct and have no extra spaces.
    2.  Ensure the names in the `.env` file (`DISCORD_TOKEN`, `GROQ_API_KEY`, `JENTIC_AGENT_API_KEY1`) exactly match the names in the script.

- **"Could not find a 'discord' tool" Error**:
    1.  This means your Jentic API key does not have permission to access a tool with "discord" in its name.
    2.  Log in to your Jentic account and ensure the Discord tool/API is enabled for your key.

- **`503 Service Unavailable` or `Connection refused` Errors**:
    1.  This is a network issue, not a code problem.
    2.  Check the status page for the relevant service (e.g., Groq).
    3.  Temporarily disable any firewalls or VPNs to see if they are blocking the connection.
    4.  Try running the bot from a different network (e.g., a mobile hotspot).
