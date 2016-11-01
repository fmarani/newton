from .core import *
from .storage import backup_resources
import argparse

parser = argparse.ArgumentParser(description='Newton - Decentralized Twitter')
parser.add_argument('-i','--init', help='Initialize basic info', action="store_true")
parser.add_argument('-b','--backup', help='Backup current storage info locally', action="store_true")
parser.add_argument('-f','--follow', help='Start following a profile')
parser.add_argument('-m','--message', help='Send a Newt message')
parser.add_argument('-r','--reply', help='Reply to a Newt message', nargs=2, metavar=("URL", "MESSAGE"))
parser.add_argument('-n','--repost', help='Repost (renewt) a Newt message', nargs=1, metavar=("URL", ))
parser.add_argument('-l','--like', help='Like a Newt message', nargs=1, metavar=("URL", ))
#parser.add_argument('-b','--bar', help='Description for bar argument', required=True)
args = parser.parse_args()

if args.init:
    init()
elif args.backup:
    wait(backup_resources())
elif args.follow:
    wait(follow(args.follow))
elif args.message:
    wait(post_newt(args.message))
elif args.reply:
    wait(post_reply(args.reply[0], args.reply[1]))
elif args.repost:
    wait(post_renewt(args.repost[0]))
elif args.like:
    wait(post_like(args.like[0]))
else:
    wait_timeline()
