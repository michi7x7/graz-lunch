from textwrap import dedent
from dataclasses import dataclass
from logging import getLogger

log = getLogger(__name__)


from .teams_api import teams


@dataclass()
class Message:
    text: str = ""
    markdown: str = ""
    files: list = None

    def __str__(self):
        if self.markdown:
            return self.markdown
        else:
            return self.text


def fetch_mittag_at(restaurant_id):
    from requests import get
    from bs4 import BeautifulSoup

    resp = get(f"https://www.mittag.at/r/{restaurant_id}")
    resp.raise_for_status()

    html = BeautifulSoup(resp.content.decode("utf-8"), features="lxml")
    menu = html.find("div", {'class': "current-menu"})
    return "".join(str(x) for x in menu.children)


def get_intro() -> Message:
    markdown = dedent("""
        # Todays Lunch Menu! 🍽️
        Hi all, here is today's lunch menu. I hope this helps 😃
    """)

    return Message(text=markdown, markdown=markdown)


def get_mangolds_link() -> str:
    from requests import get
    from bs4 import BeautifulSoup
    from datetime import date
    import re

    resp = get(f"https://www.mangolds.com/restaurant-cafe/mangolds-griesgasse/")
    resp.raise_for_status()

    html = BeautifulSoup(resp.content.decode("utf-8"), features="lxml")

    menus = (x for x in html.find_all("a") if "Speiseplan" in x["href"])
    regex = re.compile(r"(\d+)\.(\d+)\D+(\d+).(\d+)")

    for menu in menus:
        m = regex.match(menu.get_text())
        st = date.today().replace(day=int(m.group(1)), month=int(m.group(2)))
        en = date.today().replace(day=int(m.group(3)), month=int(m.group(4)))
        if en < st:
            en.replace(year=en.year+1)

        if st <= date.today() <= en:
            return menu['href']

    return None


def get_mangolds() -> Message:
    from textwrap import dedent
    try:
        # get_mangolds_link()
        href = "https://www.mangolds.com/restaurant-cafe/mangolds-griesgasse/"
        if href is None:
            raise RuntimeError("link not found")

        markdown = dedent(f"""
            ## Mangolds
            [This weeks menu]({href})
        """)
    except:
        href = None
        markdown = dedent(f"""
            ## Mangolds
            Could not get a link for today's menu, sorry 🙏
        """)

    return Message(text=markdown, markdown=markdown)  #, files=[href])


def get_outro() -> Message:
    markdown = dedent("""
        ## Some other options, that I cannot yet understand
        []
    """)


def get_mittag_at(id: str, title: str) -> Message:
    try:
        menu = fetch_mittag_at(id)

        markdown = dedent(f"""
                ## {title}
                {menu}
            """)

        return Message(text=markdown, markdown=markdown)
    except:
        log.error(f"could not fetch menu from {id}", exc_info=True)
        return None


def get_messages() -> [Message]:
    ret = [
        get_intro(),
        get_mittag_at("rondo", "Rondo"),
        get_mittag_at("die-scherbe", "Die Scherbe"),
        get_mittag_at("kunsthauscafe", "Kunsthauscafe"),
        get_mangolds(),
    ]

    return filter(lambda x: x is not None, ret)


def send_debug(personal_email):
    messages = get_messages()
    for message in messages:
        teams.messages.create(toPersonEmail=personal_email, **message.__dict__)


def send_all():
    rooms = teams.rooms.list()
    messages = list(get_messages())

    for room in rooms:
        if room.type == "direct":
            continue

        log.info(f"Sending Messages to {room.title} with id {room.id}")
        for message in messages:
            teams.messages.create(roomId=room.id, text=message.text, markdown=message.markdown)
