from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
import discord


class Database(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        load_dotenv()
        self.conn = sqlite3.connect("ScrimSchedulerDB.db")
        self.cur = self.conn.cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS scrimteams (
                server_id BIGINT NOT NULL,
                team_id SERIAL PRIMARY KEY,
                team_name TEXT NOT NULL,
                scrim_blocks TEXT
        );"""
        )
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS scrimplayers (
                team_id INTEGER REFERENCES scrimteams(team_id),
                user_id BIGINT NOT NULL,
                availability ,
                PRIMARY KEY (team_id, user_id)
        );"""
        )
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS scrimmanagers (
                team_id INTEGER REFERENCES scrimteams(team_id),
                user_id BIGINT NOT NULL,
                PRIMARY KEY (team_id, user_id)
        );"""
        )
        self.conn.commit()

    def create_team(self, server_id, team_name):
        self.cur.execute(
            """
                INSERT INTO scrimteams (server_id, team_name) VALUES (?, ?)
            """,
            (server_id, team_name),
        )
        self.conn.commit()

    def set_team_scrim_blocks(self, team_id, blocks):
        self.cur.execute(
            """
                UPDATE scrimteams
                SET scrim_blocks = ?
                WHERE team_id = ?
                """,
            (blocks, team_id),
        )
        self.conn.commit()

    # ASSUMES SCRIM BLOCKS AND TEAM EXIST
    def get_team_scrim_blocks(self, team_id):
        self.cur.execute(
            """
                SELECT scrim_blocks
                FROM scrimteams
                WHERE team_id = ?
            """,
            (team_id,),
        )
        row = self.cur.fetchone()
        return row[0] if row else ""

    def get_teams_from_user_id(self, user_id):
        self.cur.execute(
            """
                SELECT team_id, team_name FROM scrimteams                
                LEFT JOIN scrimplayers ON scrimteams.team_id = scrimplayers.team_id
                LEFT JOIN scrimmanagers ON scrimteams.team_id = scrimmanagers.team_id
                WHERE scrimplayers.user_id = ? OR scrimmanagers.user_id = ?;
            """,
            (user_id, user_id),
        )
        return self.cur.fetchall()

    def get_all_teams_from_server_id(self, server_id):
        self.cur.execute(
            """
            SELECT team_id, team_name FROM scrimteams
            WHERE server_id = ?;""",
            (server_id,),
        )
        res = self.cur.fetchall()
        return res

    def is_manager(self, team_id: int, user_id: int) -> bool:
        self.cur.execute(
            "SELECT 1 FROM scrimmanagers WHERE team_id = ? AND user_id = ?;",
            (team_id, user_id),
        )
        return self.cur.fetchone() is not None

    @discord.app_commands.command(name="testdb")
    async def print_all_teams(self, interaction: discord.Interaction):
        content = ""
        self.cur.execute(
            """
                SELECT * FROM scrimteams
            """
        )
        res = self.cur.fetchall()
        for i in res:
            content += f"{i}\n"
        await interaction.response.send_message(content)


async def setup(bot):
    await bot.add_cog(Database(bot))
