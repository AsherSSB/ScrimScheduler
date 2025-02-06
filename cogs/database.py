from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
import discord


class Database(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        load_dotenv()
        self.conn = sqlite3.connect("ScrimSchedulerDB")
        self.cur = self.conn.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS scrimteams (
                server_id BIGINT NOT NULL,
                team_id SERIAL PRIMARY KEY,
                team_name VARCHAR(100) NOT NULL,
                players BIGINT[],
                managers BIGINT[],
                scrim_blocks VARCHAR[]
        );""")
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS scrimplayers (
                team_id INTEGER REFERENCES scrimteams(team_id),
                user_id BIGINT,
                availability SMALLINT[],
                PRIMARY KEY (team_id, user_id)
        );""")
        self.conn.commit()

    # TODO: query to find all teams where user is a manager or player

    def get_all_teams(self, server_id):
        self.cur.execute("""
            SELECT team_id, team_name FROM scrimteams
            WHERE server_id = ?;""", (server_id,))
        res = self.cur.fetchall()
        return res


async def setup(bot):
    await bot.add_cog(Database(bot))
