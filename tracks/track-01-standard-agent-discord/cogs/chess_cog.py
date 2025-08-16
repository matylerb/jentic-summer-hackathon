import discord
from discord.ext import commands
from discord import app_commands
import chess

# --- Chess Game Cog ---

# Dictionary to store active chess games { channel_id: game_data }
active_games = {}

def format_board(board):
    """Formats the chess board with Unicode pieces for display in Discord."""
    pieces = {
        'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
        'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
        '.': '•'
    }
    board_str = str(board)
    unicode_board = ""
    for char in board_str:
        if char in pieces:
            unicode_board += pieces[char]
        else:
            unicode_board += char
    return f"```\n{unicode_board}\n```"

class ChessCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    chess_group = app_commands.Group(name="chess", description="Commands for playing chess.")

    @chess_group.command(name="start", description="Challenge a user to a game of chess.")
    @app_commands.describe(opponent="The user you want to challenge.")
    async def start_chess(self, interaction: discord.Interaction, opponent: discord.Member):
        channel_id = interaction.channel_id
        if channel_id in active_games:
            await interaction.response.send_message("A game is already in progress in this channel.", ephemeral=True)
            return
        
        if opponent.bot:
            await interaction.response.send_message("You cannot challenge a bot to a chess game.", ephemeral=True)
            return

        if opponent == interaction.user:
            await interaction.response.send_message("You cannot challenge yourself to a chess game.", ephemeral=True)
            return

        # Create a new game
        active_games[channel_id] = {
            "board": chess.Board(),
            "white": interaction.user,
            "black": opponent,
            "turn": interaction.user # White goes first
        }

        embed = discord.Embed(
            title="♟️ Chess Game Started! ♟️",
            description=f"{interaction.user.mention} (White) has challenged {opponent.mention} (Black) to a game of chess.",
            color=discord.Color.dark_gold()
        )
        embed.add_field(name="Turn", value=f"It's {interaction.user.mention}'s turn (White).")
        embed.add_field(name="Board", value=format_board(active_games[channel_id]["board"]), inline=False)
        
        await interaction.response.send_message(embed=embed)

    @chess_group.command(name="move", description="Make a move in the current chess game.")
    @app_commands.describe(move="Your move in Standard Algebraic Notation (e.g., e4, Nf3, O-O).")
    async def move_chess(self, interaction: discord.Interaction, move: str):
        channel_id = interaction.channel_id
        if channel_id not in active_games:
            await interaction.response.send_message("There is no chess game in progress in this channel.", ephemeral=True)
            return

        game = active_games[channel_id]
        board = game["board"]

        if interaction.user != game["turn"]:
            await interaction.response.send_message("It's not your turn.", ephemeral=True)
            return

        try:
            board.push_san(move)
        except chess.IllegalMoveError:
            await interaction.response.send_message(f"'{move}' is not a valid move. Please use Standard Algebraic Notation.", ephemeral=True)
            return

        # Switch turns
        game["turn"] = game["black"] if game["turn"] == game["white"] else game["white"]

        # Check for game over conditions
        if board.is_game_over():
            result_text = ""
            if board.is_checkmate():
                winner = game['white'] if board.turn == chess.BLACK else game['black']
                result_text = f"Checkmate! {winner.mention} wins!"
            elif board.is_stalemate():
                result_text = "Stalemate! The game is a draw."
            elif board.is_insufficient_material():
                result_text = "Draw due to insufficient material."
            else:
                result_text = "The game is over. It's a draw."

            embed = discord.Embed(title="♟️ Game Over! ♟️", description=result_text, color=discord.Color.red())
            embed.add_field(name="Final Board", value=format_board(board), inline=False)
            await interaction.response.send_message(embed=embed)
            del active_games[channel_id] # Clean up the game
            return

        # If game is not over, show the updated board
        embed = discord.Embed(
            title="♟️ Chess Game ♟️",
            description=f"Move `{move}` made by {interaction.user.mention}.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Turn", value=f"It's {game['turn'].mention}'s turn.")
        if board.is_check():
             embed.set_footer(text="Check!")
        embed.add_field(name="Board", value=format_board(board), inline=False)
        await interaction.response.send_message(embed=embed)

    @chess_group.command(name="board", description="Display the current chess board.")
    async def board_chess(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        if channel_id not in active_games:
            await interaction.response.send_message("There is no chess game in progress in this channel.", ephemeral=True)
            return

        game = active_games[channel_id]
        embed = discord.Embed(title="♟️ Current Chess Board ♟️", color=discord.Color.light_gray())
        embed.add_field(name="Turn", value=f"It's {game['turn'].mention}'s turn.")
        embed.add_field(name="Board", value=format_board(game["board"]), inline=False)
        await interaction.response.send_message(embed=embed)

    @chess_group.command(name="resign", description="Resign from the current chess game.")
    async def resign_chess(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        if channel_id not in active_games:
            await interaction.response.send_message("There is no chess game in progress in this channel.", ephemeral=True)
            return

        game = active_games[channel_id]
        if interaction.user != game["white"] and interaction.user != game["black"]:
            await interaction.response.send_message("You are not a player in this game.", ephemeral=True)
            return

        winner = game["black"] if interaction.user == game["white"] else game["white"]
        
        embed = discord.Embed(
            title="♟️ Game Over! ♟️",
            description=f"{interaction.user.mention} has resigned. {winner.mention} wins!",
            color=discord.Color.red()
        )
        embed.add_field(name="Final Board", value=format_board(game["board"]), inline=False)
        await interaction.response.send_message(embed=embed)
        del active_games[channel_id]


async def setup(bot: commands.Bot):
    await bot.add_cog(ChessCog(bot))