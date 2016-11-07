from .core import *
from .storage import backup_resources
from . import twitter as tw
from . import async_http
import argparse
import asyncio

parser = argparse.ArgumentParser(description='Newton - Decentralized Twitter')
parser.add_argument('-i', '--init', help='Initialize basic info', action="store_true")
parser.add_argument('-c', '--config', help='config.py import path', default="config")
parser.add_argument('-b', '--backup', help='Backup current storage info locally', action="store_true")
parser.add_argument('-f', '--follow', help='Start following a profile')
parser.add_argument('-m', '--message', help='Send a Newt message')
parser.add_argument('-r', '--reply', help='Reply to a Newt message', nargs=2, metavar=("URL", "MESSAGE"))
parser.add_argument('-n', '--repost', help='Repost (renewt) a Newt message', nargs=1, metavar=("URL", ))
parser.add_argument('-l', '--like', help='Like a Newt message', nargs=1, metavar=("URL", ))
parser.add_argument('--twitter-auth', help='Authorize twitter access', action="store_true")
args = parser.parse_args()

config.setup(args.config)
async_http.init()

loop = asyncio.get_event_loop()

if config.TWITTER_INTEGRATION:
    tw.init(loop, async_http.session)

if args.init:
    init()
elif args.twitter_auth:
    tw.authorize()
elif args.backup:
    wait(backup_resources(), loop)
elif args.follow:
    wait(follow(args.follow), loop)
elif args.message:
    wait(post_newt(args.message, loop), loop)
elif args.reply:
    wait(post_reply(args.reply[0], args.reply[1]), loop)
elif args.repost:
    wait(post_renewt(args.repost[0]), loop)
elif args.like:
    wait(post_like(args.like[0]), loop)
else:
    wait_timeline(loop)

async_http.destroy()
