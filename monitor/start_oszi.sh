#!/usr/bin/bash 
#sleep 3;
sudo /opt/netns/create 18
CMD="python3 /opt/LibreLight/ASP/monitor/oszi_grid.py"  
/opt/netns/exec --id=18 --cmd="xterm -e screen $CMD" &



