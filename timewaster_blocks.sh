#!/bin/bash
#
# Stop the names of just some of the many websites that I have problems with.
# Run this at system startup to avoid the pit of news-seeking. This is
# really just about breaking the habits

declare -a arr=("wral.com" "wncn.com" "abc11.com" 
"facebook.com" "twitter.com" "imgur.com" "gfycat.com"
"news.google.com" "reddit.com" "nfl.com" "si.com" "espn.com"
"sbnation.com" "bleacherreport.com" "sportingnews.com"
"drudgereport.com")

for i in "${arr[@]}"
do
   iptables -I INPUT -s $i -d 0/0 -j DROP
done

