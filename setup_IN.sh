#!/usr/bin/bash

sudo sh /home/pi/ASP/netns.sh 24 
sudo ip netns exec blue224 su pi -c 'screen -d -m -S ASP_IN sh /home/pi/ASP/map14_in_to0.sh'
