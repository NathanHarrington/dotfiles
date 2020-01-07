
For details on Bose QuietControl 30 see the auto_bluetooth.sh file

On the u430, there are no audio-next, previous, or play buttons etc.

Open gnome keyboard settings and set shortcuts:
Next Track  Ctrl+Alt+Mod4+]
Play (or Play/Pause) Ctrl+Alt+Mod4+l
Previous Track  Ctrl+Alt+Mod4+[


After you start cmus for the first time, make sure to run:
    :set passwd=cmuscontrolitifyouwant


Add the shortcuts for switching music focus modes in 
focus_music.sh
rocklist_only.sh
what_is_playing.sh
classical_only.sh


If operating a music service on a different computer, add the functions
    as showin in: cmus_remote_control.sh 
    
Make sure to start cmus with the --listen ip address:port option

