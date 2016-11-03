Newton - Decentralized Twitter
---

Twitter is having a lot on impact on the world and how I keep updated regarding tech and general news, but most of us love/hate it at the same time. The brevity of each message allows you to hear many voices. Unfortunately the site has been going downhill for me for some time. Speed is not impressive, Ads are annoying and irrelevant, and I generally do not like to give my data to somebody else.

In a classic "this should not be hard to rewrite" moment, I wrote my version of it. In other words, this is a simple implementation of what I imagined to be a good base for a decentralized Twitter. I called it Newton.

You will find no blockchains, bittorrent or other wizardries here. I am using tools that do not require to be online all the time, and are wide-spread.

If you feel experimental, download this and play with it. Happy Newt-ing! :)


Architecture
---

More than a classic client application, this software is more similar to a static site generator, but instead of HTML it generates JSON files. These JSON files have a specific format, and are meant to be publicly addressable with HTTP.

There are two "storage" modules now, one for local publishing (needs a web server setup) and one using Google drive (because most people have a Google account). I think having a Dropbox and an S3 module in the future would be nice.

More on this later.
