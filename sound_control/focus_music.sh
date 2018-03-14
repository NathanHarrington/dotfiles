#!/bin/bash
# Stop cmus current playing, play the handel organ concerto
cmus-remote --pause
mplayer "/home/nharrington/Downloads/refined_mp3s/G._F._Haendel_-_Organ_Concertos.mp3"
cmus-remote --play

