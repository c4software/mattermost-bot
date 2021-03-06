# -*- coding: utf-8 -*-

import random
import json
from tools.rest import callrest
from commands.libs.decorators import register_as_command

from bs4 import BeautifulSoup
from expiringdict import ExpiringDict

cache = ExpiringDict(max_len=1, max_age_seconds=3600)

from settings import REDDIT_ALL, REDDIT_IMAGE, REDDIT_LOL, REDDIT_GIF, REDDIT_OTHER


def get_reddit_random():
    # On melange les categorie principale.
    random.shuffle(REDDIT_ALL)
    # Recuperation d'un subbreddit dans les categories.
    return get_reddit(random.choice(random.choice(REDDIT_ALL)))


def get_reddit(subreddit):
    try:
        data = \
        callrest(domain="www.reddit.com", port=443, ssl=True, path="/r/{0}/new/.json".format(subreddit), params={})[2]
        return random.choice(json.loads(data).get("data").get("children")).get("data")
    except Exception as e:  # pragma: no cover
        print(e)
        return "Désolé, aucun résultat"


def return_md(message, preview=False):
    url = message.get("url")
    if preview and ("jpeg" in url or "jpg" in url or "png" in url or "gif" in url) and "gifv" not in url:
        return "{0} : ![image]({1})".format(message.get("title"), url)
    else:
        return "{0} : {1}".format(message.get("title"), url)


def get_redditlist(type_reddit="all"):
    cache_key = "redditlist_{0}".format(type_reddit)
    if cache_key not in cache:
        result = callrest(domain="redditlist.com", type="GET", path="/{0}".format(type_reddit), params={})
        if result[0] == 200:
            cache[cache_key] = result[2]
        else:  # pragma: no cover
            return get_reddit_random()

    soup = BeautifulSoup(cache[cache_key], "html.parser")
    links = soup.find_all("div", class_="listing-item")
    if len(links) > 0:
        subReddit = random.choice(links).get("data-target-subreddit", "")
        return get_reddit(subReddit)
    else:  # pragma: no cover
        return get_reddit_random()


@register_as_command("random", "Retourne un résultat aléatoire depuis redditlist", "Reddit")
def cmd_random(msg):
    data = get_redditlist("sfw")
    return return_md(data, False)


@register_as_command("nsfw", "Retourne un résultat depuis une séléction NSFW", "Reddit")
def cmd_nsfw(msg):
    return return_md(get_redditlist("nsfw"), False)


@register_as_command("image", "Retourne une image de reddit (sfw)", "Reddit")
def cmd_image(msg):
    return return_md(get_reddit(random.choice(REDDIT_IMAGE)), msg.get("preview", False))


@register_as_command("cute", "Un chat ?! Où un chat ?", "Reddit")
def cmd_cute(msg):
    return return_md(get_reddit(random.choice(REDDIT_LOL)), msg.get("preview", False))


@register_as_command("top10", "Top10 des liens publiés sur Reddit sur la dernière heure", "Reddit")
def cmd_top10(msg):
    return_values = []
    try:
        data = callrest(domain="www.reddit.com", port=443, ssl=True, path="/top/.json",
                        params={"limit": 10, "sort": "top", "t": "hour"})[2]
        data = json.loads(data).get("data").get("children")

        for element in data:
            try:
                return_values.append("{title} : {url}".format(**element["data"]))
            except:  # pragma: no cover
                pass

        return "Top10 : \r\n- {0}".format("\r\n- ".join(return_values))
    except Exception as e:  # pragma: no cover
        raise Exception(e)
