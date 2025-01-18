import discord
from discord.ext import commands
import psycopg2
import os
from dotenv import load_dotenv


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_dotenv()
        password = os.getenv('DB_PASS')
        self.conn = psycopg2.connect(database="SavvyRPG",
                                     host="localhost",
                                     user="postgres",
                                     password=f"{password}",
                                     port="5432")
        self.cur = self.conn.cursor()
        # TODO: initialize tables (team serial/userid primary keys)


async def setup(bot):
    await bot.add_cog(Database(bot))


