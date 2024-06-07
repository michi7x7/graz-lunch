from dotenv import load_dotenv
import os

from webexteamssdk import WebexTeamsAPI

load_dotenv()
teams = WebexTeamsAPI(access_token=os.getenv("WEBEX_TEAMS_ACCESS_TOKEN"))
