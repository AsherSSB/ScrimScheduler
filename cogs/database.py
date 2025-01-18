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
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS scrimteams (
                server_id BIGINT NOT NULL,
                team_id SERIAL PRIMARY KEY,
                team_name VARCHAR(100) NOT NULL,
                players BIGINT[],
                scrim_blocks VARCHAR[]
            );

            CREATE TABLE IF NOT EXISTS scrimplayers (
                user_id BIGINT PRIMARY KEY,
                team_id INTEGER REFERENCES scrimteams(team_id),
                team_name VARCHAR(100) NOT NULL,
                availability SMALLINT[]
        );
    """)
        self.conn.commit()


async def setup(bot):
    await bot.add_cog(Database(bot))


