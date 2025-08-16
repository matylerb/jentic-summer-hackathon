import os
import discord
from discord.ext import commands
from groq import AsyncGroq
import json
import wikipediaapi
from dotenv import load_dotenv
import asyncio
import jentic

# --- Configuration and Setup ---

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
JENTIC_API_KEY = os.getenv("JENTIC_API_KEY")

# Check for missing keys
if not all([DISCORD_TOKEN, GROQ_API_KEY]):
    raise ValueError("One or more required API keys are missing from your .env file.")

# Initialize the Groq client
groq_client = AsyncGroq(api_key=GROQ_API_KEY)

# Initialize the Wikipedia API library
wiki_wiki = wikipediaapi.Wikipedia('DiscordBot/1.0', 'en')

# --- Tool Definition ---

def search_wikimedia(query: str):
    """
    Searches for a page on Wikimedia (Wikipedia) and returns a summary.
    Args:
        query: The search term or page title to look up.
    """
    print(f"Executing Wikimedia search for: {query}")
    page = wiki_wiki.page(query)
    if not page.exists():
        return f"Could not find a Wikimedia page for '{query}'."
    return f"Title: {page.title}\nSummary: {page.summary[0:500]}..."

# --- Groq Tool Schema ---

wikimedia_tool = {
    "type": "function",
    "function": {
        "name": "search_wikimedia",
        "description": "Searches for a page on Wikimedia (Wikipedia) and returns a summary.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search term or page title to look up."
                }
            },
            "required": ["query"],
        },
    },
}

SYSTEM_PROMPT = """
You are a helpful and resourceful assistant running inside Discord.
- You must use the provided tools to answer questions and perform tasks.
- When you have a final answer, present it clearly and concisely.
- You remember the conversation history. Use it to answer follow-up questions.
"""

# --- Discord Bot Logic ---

# Use commands.Bot for slash command support
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help') # Remove the default help command to avoid conflicts

# Store conversation history per user
conversation_history = {}

@bot.event
async def on_ready():
    """Event handler for when the bot has connected to Discord."""
    print(f"We have logged in as {bot.user}")
    print("Bot is ready. Use !sync to register slash commands.")

@bot.command(name="help")
async def help_command(ctx):
    """Shows a general help message for all bot commands."""
    embed = discord.Embed(
        title="🤖 Bot Help 🤖",
        description="Here are all the available commands:",
        color=discord.Color.dark_purple()
    )
    embed.add_field(name="General Commands", value="`----------------`", inline=False)
    embed.add_field(name="`!help`", value="Shows this help message.", inline=True)
    embed.add_field(name="`!sync`", value="Syncs slash commands (owner only).", inline=True)

    embed.add_field(name="Slash Commands", value="`----------------`", inline=False)
    embed.add_field(name="`/wiki <query>`", value="Ask the AI agent a question. It can search Wikipedia for answers.", inline=False)
    
    embed.add_field(name="Chess Commands (Slash)", value="`----------------`", inline=False)
    embed.add_field(name="`/chess`", value="Starts a new game of chess.", inline=True)
    embed.add_field(name="`/move <move>`", value="Makes a move in the current game.", inline=True)
    embed.add_field(name="`/board`", value="Displays the current board.", inline=True)
    embed.add_field(name="`/reset`", value="Resets the current game.", inline=True)
    embed.add_field(name="`/chesshelp`", value="Shows detailed help for chess commands.", inline=True)

    embed.set_footer(text="Enjoy the bot!")
    await ctx.send(embed=embed)

@bot.tree.command(name="helpme", description="Shows a general help message for the bot.")
async def help_me(interaction: discord.Interaction):
    """Shows a general help embed for all bot commands."""
    embed = discord.Embed(
        title="🤖 Bot Help 🤖",
        description="Here are all the available commands:",
        color=discord.Color.dark_purple()
    )
    embed.add_field(name="Agent Commands", value="`----------------`", inline=False)
    embed.add_field(name="`/wiki <query>`", value="Ask the AI agent a question. It can search Wikipedia for answers.", inline=True)
    
    embed.add_field(name="Chess Commands", value="`----------------`", inline=False)
    embed.add_field(name="`/chess`", value="Starts a new game of chess.", inline=True)
    embed.add_field(name="`/move <move>`", value="Makes a move in the current game.", inline=True)
    embed.add_field(name="`/board`", value="Displays the current board.", inline=True)
    embed.add_field(name="`/reset`", value="Resets the current game.", inline=True)
    embed.add_field(name="`/chesshelp`", value="Shows detailed help for chess commands.", inline=True)

    embed.set_footer(text="Enjoy the bot!")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="wiki", description="Ask the agent a question that may require a Wikimedia search.")
async def wiki_command(interaction: discord.Interaction, *, query: str):
    """Handles the /wiki slash command."""
    await interaction.response.defer()

    try:
        user_id = interaction.user.id
        print(f"Starting agent loop for user {user_id} with query: {query}")

        # Get or create conversation history
        if user_id not in conversation_history:
            conversation_history[user_id] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
        
        conversation_history[user_id].append({"role": "user", "content": query})
        messages = conversation_history[user_id]

        # Initial call to Groq
        response = await groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            tools=[wikimedia_tool],
            tool_choice="auto"
        )
        response_message = response.choices[0].message

        # Loop to handle tool calls
        while response_message.tool_calls:
            await interaction.edit_original_response(content=f"🤖 Calling tool: `{response_message.tool_calls[0].function.name}`...")
            
            messages.append(response_message)

            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                if function_name != "search_wikimedia":
                    continue

                function_args = json.loads(tool_call.function.arguments)
                tool_query = function_args.get("query")
                
                tool_result = await bot.loop.run_in_executor(
                    None, 
                    lambda: search_wikimedia(tool_query)
                )

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": tool_result,
                })

            await interaction.edit_original_response(content="🤖 Analyzing tool results...")
            second_response = await groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages
            )
            response_message = second_response.choices[0].message

        result = response_message.content
        conversation_history[user_id].append({"role": "assistant", "content": result})

        print(f"Agent finished. Result: {result}")

        embed = discord.Embed(
            title=f"Query: {query}",
            description=result,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Powered by Groq, Jentic and Wikimedia")

        await interaction.followup.send(embed=embed)

    except Exception as e:
        print(f"An error occurred: {e}")
        error_embed = discord.Embed(
            title="An Error Occurred",
            description=f"Sorry, an error occurred while processing your request: {e}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=error_embed)

@bot.command()
@commands.is_owner()
async def sync(ctx: commands.Context):
    """Syncs slash commands to the current guild for immediate updates."""
    try:
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(synced)} slash command(s) to this server.")
        print(f"Synced {len(synced)} command(s) to guild: {ctx.guild.name} (ID: {ctx.guild.id})")
    except Exception as e:
        await ctx.send(f"Failed to sync commands: {e}")
        print(f"Error syncing commands: {e}")

# --- Main Entry Point ---

async def main():
    """Main function to load cogs and run the bot."""
    if not os.path.exists("cogs"):
        os.makedirs("cogs")
        
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Loaded cog: {filename}")

    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())

