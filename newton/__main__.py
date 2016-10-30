from .core import *
from .storage import backup_resources
import argparse

parser = argparse.ArgumentParser(description='Newton - Decentralized Twitter')
parser.add_argument('-i','--init', help='Initialize basic info', action="store_true")
parser.add_argument('-b','--backup', help='Backup current storage info locally', action="store_true")
parser.add_argument('-f','--follow', help='Start following a profile')
parser.add_argument('-m','--message', help='Send a Newt message')
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
else:
    wait_timeline()
