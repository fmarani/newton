from peony import PeonyClient
from newton import config
from datetime import datetime


def authorize():
    from peony.oauth_dance import oauth_dance
    consumer_key = config.TWITTER_APP_CREDENTIALS['CONSUMER_KEY']
    consumer_secret = config.TWITTER_APP_CREDENTIALS['CONSUMER_SECRET']
    tokens = oauth_dance(consumer_key, consumer_secret)
    conf = {
            'ACCESS_TOKEN': tokens['access_token'],
            'ACCESS_TOKEN_SECRET': tokens['access_token_secret'],
            }
    print(conf)
    print("Please write this data in the config file")


client = None

def init(loop, client_session):
    global client
    client = get_client(loop, client_session)

def get_client(loop, client_session):
    consumer_key = config.TWITTER_APP_CREDENTIALS['CONSUMER_KEY']
    consumer_secret = config.TWITTER_APP_CREDENTIALS['CONSUMER_SECRET']
    access_token = config.TWITTER_USER_CREDENTIALS['ACCESS_TOKEN']
    access_token_secret = config.TWITTER_USER_CREDENTIALS['ACCESS_TOKEN_SECRET']
    return PeonyClient(consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            loop=loop,
            session=client_session)


async def post_tweet(text):
    return await client.api.statuses.update.post(status=text)


async def post_reply(replyToUrl, text):
    status_id = replyToUrl.strip("/").split("/")[-1]
    return await client.api.statuses.update.post(status=text, in_reply_to_status_id=status_id)


async def post_retweet(tweet_url):
    status_id = tweet_url.strip("/").split("/")[-1]
    poster = client.api.statuses.retweet[status_id]
    return await poster.post(id=status_id)


async def post_like(like_url):
    status_id = like_url.strip("/").split("/")[-1]
    return await client.api.favorites.create.post(id=status_id)


async def follow(user_url):
    screen_name = user_url.strip("/").split("/")[-1]
    return await client.api.friendships.create.post(screen_name=screen_name)

    
async def timeline():
    response = await client.api.statuses.home_timeline.get(count=200)

    newts = []
    for tweet in response:
        newt = {
            "handle": tweet.user.screen_name,
            "msg": tweet.text,
            "datetime": datetime.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
            }

        if tweet.in_reply_to_status_id or tweet.in_reply_to_user_id:
            newt['type'] = "reply"
            if tweet.in_reply_to_status_id:
                newt['replyToUrl'] = "https://twitter.com/{}/status/{}".format(tweet.user.screen_name, tweet.in_reply_to_status_id)
            else:
                newt['replyToUrl'] = "https://twitter.com/{}".format(tweet.user.screen_name)
        else:
            newt['type'] = "newt"

        newts.append(newt)

    return newts
