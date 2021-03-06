#!/bin/sh
#
# Stop the names of just some of the many websites that I have problems with.
# Run this at system startup to avoid the pit of news-seeking. This is
# really just about breaking the habits. This is desinged to be run in
# cron's root tab every hour. So if you really need just a quick access
# to reddit or facebook, remove the entry from the /etc/hosts file as
# root and it should be available again.

declare -a arr=("wral.com" "wncn.com" "abc11.com"
"cnn.com" "arcgis.com" "cnbc.com" 
"facebook.com" "twitter.com" "imgur.com" "gfycat.com"
"news.google.com" "reddit.com" "nfl.com" "si.com" "espn.com"
"sbnation.com" "bleacherreport.com" "sportingnews.com"
"foxnews.com" "drudgereport.com" "newsobserver.com"
"news.ycombinator.com" "www.nhc.noaa.gov" "cbs.com"
"theringer.com" "profootballfocus.com" "profootballreference.com"
"cbssports.com" "shutterstock.com", "profootballtalk.nbcsports.com"
"nbcsports.com" "9gag.com" "footballoutsiders.com")

echo "127.0.0.1 localhost.localdomain localhost" > /etc/hosts
echo "::1     localhost6.localdomain6 localhost6" >> /etc/hosts
echo "216.239.38.120     www.google.com # force safesearch " >> /etc/hosts


for i in "${arr[@]}"
do
    echo "0.0.0.0    www.$i" >> /etc/hosts
    echo "0.0.0.0    $i" >> /etc/hosts
    echo "::0    www.$i" >> /etc/hosts
    echo "::0    $i" >> /etc/hosts
done

