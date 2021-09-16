# Add this to a keyboard shortcut of ctrl-alt-mod-h, with the command:
# /usr/bin/mate-terminal --full-screen -- sh -c \
#    '/home/nharrington/projects/dotfiles/autokeyboard/breathe.sh'

figlet "Breathe"
function relaxing_breathing() {
 function mantra() {
 if which lolcat &> /dev/null; then
 echo -en "\r\033[K $1" | lolcat 
 else
 echo -en "\r\033[K $1"
 fi
 }

 function sleepcount() {
 for i in {1..4}; do echo -en " $i" && sleep 1; done
 }
 while true; do
 mantra "Breathe in"
 sleepcount
 mantra "Hold air in your lungs"
 sleepcount
 mantra "Exhale"
 sleepcount
 mantra "Hold your breath, lungs emptied"
 sleepcount
 done
 }

relaxing_breathing
