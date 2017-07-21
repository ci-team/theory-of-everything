#!/usr/bin/env python3

'''Export topics from NodeBB forum into md format

* needs local access to the redis database;
* exports only topics from predefined list of categories;
* adds metadata section to every article.

'''


import redis
import logging
import datetime
import os

logging.basicConfig(level=logging.DEBUG)

R = redis.Redis("localhost", encoding='utf-8', decode_responses=True)

LINK_TEMPLATE="https://quantum-integration.org/topic/{slug}"

ARTICLE_TEMPLATE = \
'''---
slug: {slug}
title: {title}
author: {author}
date: {date}
tags: {tags}
categories: {categories}
link: {link}
---

{content}

'''

CATEGORIES = {
    "3": {
        "name": "Knowledge Base",
        "path": "kb",
    },
    "6": {
        "name": "CI Book",
        "path": "ci-book",
    },
}

def get_users():
    users = {}
    for key in R.scan_iter("uid:*:topics"):
        uid = key.split(':')[1]
        users[uid] = R.hget("user:%s" % uid, "username")

    return users

USERS = get_users()

def get_date(ts_string):
    return ts_string
    return datetime.datetime.fromtimestamp(
        int(ts_string)
    ).strftime('%Y-%m-%d %H:%M:%S')

for cid, cdata in CATEGORIES.items():
    tids = R.zscan_iter("cid:%s:tids" % cid)
 
    for tid, ts in tids:
        topic = R.hgetall("topic:%s" % tid)
        logging.debug(topic)
        logging.info("Rendering topic with tid %s" % tid)

        article = ARTICLE_TEMPLATE.format(
            slug = topic['slug'],
            title = topic['title'],
            author = USERS[topic['uid']],
            date = get_date(topic['timestamp']),
            tags = ",".join(sorted(R.smembers("topic:%s:tags" % tid))),
            categories = cdata["name"],
            link = LINK_TEMPLATE.format(slug=topic['slug']),
            content = R.hget("post:%s" % topic["mainPid"], "content"),
        )
        
        filename = "{cpath}/{slug}.md".format(
            cpath = cdata["path"],
            slug=topic["slug"],
        )
        logging.info("Publishing to file %s" % filename)

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, "w") as f:
            f.write(article)
