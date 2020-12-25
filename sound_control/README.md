
For details on Bose QuietControl 30 see the auto_bluetooth.sh file

On the u430, there are no audio-next, previous, or play buttons etc.

Open mate keyboard settings and add custom shortcuts below. Reusing the
next/play audio shortcuts will not work.
# ctrl+alt+Mod4+pagedown <full_path>/cmus_remote_control.sh seek_forward
# ctrl+alt+Mod4+pageup <full_path>/cmus_remote_control.sh seek_backward
#
# ctrl+alt+Mod4+] <full_path>/cmus_remote_control.sh next
# ctrl+alt+Mod4+[ <full_path>/cmus_remote_control.sh back


After you start cmus for the first time, make sure to run:
    :set passwd=cmuscontrolitifyouwant


Add the shortcuts for switching music focus modes in 
set_chrome_volumes.sh*   ctrl+alt+Mod4+c
set_music_volumes.sh*    ctrl+alt+Mod4+m
what_is_playing.sh       ctrl+alt+mod4+w
focus_music.sh           ctrl+alt+mod4+f
rocklist_only.sh         ctrl+alt+mod4+r
classical_only.sh        ctrl+alt+mod4+l


If operating a music service on a different computer, add the functions
    as showin in: cmus_remote_control.sh 
    
Make sure to start cmus with the --listen ip address:port option

