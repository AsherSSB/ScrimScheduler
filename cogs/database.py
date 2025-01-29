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
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS scrimteams (
                server_id BIGINT NOT NULL,
                team_id SERIAL PRIMARY KEY,
                team_name VARCHAR(100) NOT NULL,
                players BIGINT[],
                managers BIGINT[],
                scrim_blocks VARCHAR[]
            );

            CREATE TABLE IF NOT EXISTS scrimplayers (
                team_id INTEGER REFERENCES scrimteams(team_id),
                user_id BIGINT,
                availability SMALLINT[],
                PRIMARY KEY (team_id, user_id)
            );
        """)
        self.conn.commit()

    # TODO: query to find all teams where user is a player

    def get_teams(self, server_id):
        self.cur.execute("""
            SELECT (team_id, team_name) FROM scrimteams
            WHERE server_id = %s;""", (server_id,))
        res = self.cur.fetchall()
        return res


async def setup(bot):
    await bot.add_cog(Database(bot))


