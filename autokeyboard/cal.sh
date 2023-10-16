# Add this to a keyboard shortcut of ctrl-alt-mod-c, with the command:
# /usr/bin/mate-terminal --full-screen -- sh -c \
#    '/home/nharrington/projects/dotfiles/autokeyboard/cal.sh'

cal $(date +%Y) --color=always |less -R
