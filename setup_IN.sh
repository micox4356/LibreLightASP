#!/usr/bin/bash

#sudo sh /opt/LibreLight/ASP/netns.sh 24 
#sudo ip netns exec blue224 su user -c 'screen -d -m -S ASP_IN sh /opt/LibreLight/ASP/map14_in_to0.sh'

sudo /opt/netns/create inmap14
/opt/netns/exec --id=inmap14 --cmd="screen -d -m -S ASP_IN sh /opt/LibreLight/ASP/map14_in_to0.sh"

