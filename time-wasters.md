This configuration is awesome - this truly helps focus.

Leechblock on all firefox web browsers.

Config:

First - give it an extremely long password. Something you can type in and during the entire process remind yourself over and over:

Why am I doing this?

That alone is a drastic improvement.


First Tab: 
Custom Name: INDIVIDUAL
doamin names to block:
aol.com
bleacherreport.com
cbsports.com
espn.com
news.google.com
nfl.com
si.com

Block Sun-Sat - all week
Immediately block pages

Second Tab:
GMAIL+Linkedin
mail.google.com
voice.google.com
linkedin.com

Timeframe to block:
0000-1159, 1300-2359

Block Sun-Sat - all week

Third Tab:
GOOGLE NFL
*.google.com
~football
~nfl
~panthers
~steelers

Block sun-sat all week, all time

Network Configuration

Hardware: TPLINK 450M Model No. TL-WR940N/TL-WR941ND 

The goal here is to stop all time wasters at the network level.
Specific focus includes tablets - anything with a handheld modality needs extra restrictions.

Make a logging into the router a significant speed bump.
Store the router password backwards, with spaces between the portions and with gaps with descriptions in between to make it hard to cut and paste. Make it hard to disable. Make sure you never store it in web browser password manager.

Use OpenDNS filtering dns servers:
Primary: 208.67.222.123
Secondary: 208.67.220.123

Parental control is not what you want, as it disables all internet access.
Use Access Control rules:
Deny the packets specified by any enabled access control policy to pass through the Router

Create hosts table similar to:
1	all internals		IP: 192.168.0.2 - 192.168.0.254 
2	amazon-2246b79d9	MAC: 74-75-48-4C-1A-2A 
3	kindle-f1a3129ad	MAC: 00-BB-3A-1A-B3-4A 
4	u430			MAC: 0C-8B-FD-17-03-AE 

Where amazon-* and kindle-* are tablets.

Create target table similar to:
time waster domains
	domains:	nfl.com, reddit.com, duckduckgo.com, bing.com
	You can only create groups of 4, so make multiple groups.

Then create rules table like the following:
time wasters	all internals	  time waster domains	Permanent
moretime waster	all internals	  more time wasters	Permanent
youtubekindle1	amazon-2246b79d9  youtube domain block	Permanent
youtubekindle2	kindle-f1a3129ad  youtube domain block	Permanent
all youtube 	all internals     youtube domain block	Permanent
yetmorerule	all internals	  yet more time wasters	Permanent
twtwo20180426	u430	          time wasters 20180426	Permanent
social media 	u430	          facebook and twitter	Permanent

Important to add specific rules blocking google image search on tablets. You can't block just by domain, but you can block the thumbnails effectively with:
	target description: gstatic.com	
		domain: gstatic.com
		domain: encrypted-tbn0.gstatic.com

Then setup a rule to block that target on any handheld device.

Track the time you spend on different sites. Plug in the MAC-based filtering rules at the network level and the leechblock level and the /etc/hosts level if you need to. Create those speed bumps to free yourself.

For example - how much time do you spend on wikipedia? If it's more than
5 minutes per day you're probably wasting your life with entertainment
during work hours. Block it at the network level and you will find you
can still get all the information you really need elsewhere.


Mobile device setup
Hardware: Moto E 2nd Gen Android 5.1

Force stop and disable:
Gmail
chrome
google play books
google play games
google play newsstand
hp print service plugin
talkback
wallet

Install screentime labs
App-block activate at all times:
gmail, chrome, googleapp, google play games, google play movies and tv, google play newsstand, google plus

Set monday-friday 2 min daily limit - not sure what this does, but that was the setting.

Now your phone gives you google play music, google maps for navigation, google voice for messaging and phone. 

Make sure to turn off all notifications for all apps except calendar.
For calendar, install "Calendar Snooze" free version, which will buzz repeatedly until a calendar notification is acknoledged.
