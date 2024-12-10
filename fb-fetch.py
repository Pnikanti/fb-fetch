import requests
import sys
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  

BASE_URL = "https://graph.facebook.com/v21.0"

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
USER_ID = os.getenv("USER_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def fetch(account_id: str, output_file: str):
    accs = accounts(True)["data"]
    page_access_token = None

    for acc in accs:
        if acc["id"] != account_id:
            continue

        page_access_token = acc["access_token"]
        break

    response = requests.get(f"{BASE_URL}/{account_id}/feed" +
        f"?access_token={page_access_token}"
    )

    if response.status_code != 200:
        print(response.text)
        exit(1)

    feed = response.json()["data"]
    posts = []

    for item in feed:
        if not item.get("message"):
            continue

        post = {}
        post["images"] = []
        post["videos"] = []
        post["url"] = f"https://www.facebook.com/{item['id']}"
        post["text"] = item["message"]
        post["timestamp"] = int(datetime.strptime(item["created_time"], "%Y-%m-%dT%H:%M:%S%z").timestamp())

        response = requests.get(f"{BASE_URL}/{item['id']}/attachments?access_token={page_access_token}")

        attachments = response.json()["data"]

        if not attachments:
            posts.append(post)
            continue

        attachments = attachments[0]

        if media := attachments.get("subattachments"):
            media = media["data"]
            for med in media:
                if med["type"] == "video":
                    post["videos"].append(med["media"]["source"])
                elif med["type"] == "photo":
                    post["images"].append(med["media"]["image"]["src"])
                else:
                    print(f"{med['type']} type not supported!")
        elif media := attachments.get("media"):
            post["images"].append(media["image"]["src"])

        posts.append(post)
        
    posts = json.dumps(posts, indent=4, ensure_ascii=False)
    print(posts)

    with open(output_file, "w") as file:
        file.write(posts)


def accounts(return_values = False):
    response = requests.get(f"{BASE_URL}/me/accounts" +
        f"?access_token={ACCESS_TOKEN}"
    )

    if response.status_code != 200:
        print(response.text)
        exit(1)

    res = response.json()

    if return_values:
        return res

    print(res)

def refresh():
    response = requests.get(f"{BASE_URL}/oauth/access_token" +
        f"?grant_type=fb_exchange_token" +
        f"&client_id={APP_ID}" +
        f"&client_secret={APP_SECRET}" +
        f"&fb_exchange_token={ACCESS_TOKEN}"
    )

    if response.status_code != 200:
        print(response.text)
        exit(1)

    data = response.json()
    print("> Replace .env access token with the following one️‍ 🔥")
    print(data)

def help():
    print(f"> {sys.argv[0]} --refresh to get a long lived access token")
    print(f"> {sys.argv[0]} --accounts to get all managed accounts")
    print(f"> {sys.argv[0]} <account id> <output file> to get the account's public feed")

if __name__ == "__main__":
    if (len(sys.argv) == 1):
        help()
        exit(0)

    if sys.argv[1] == "--refresh":
        refresh()
        exit(0)

    if sys.argv[1] == "--accounts":
        accounts()
        exit(0)

    if len(sys.argv) != 3:
        help()
        exit(0)

    fetch(sys.argv[1], sys.argv[2])
