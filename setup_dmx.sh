#!/usr/bin/bash
# to execute as cron job @reboot with an admin user ! not secure !

sudo su user -c 'screen -ls'
sudo su user -c 'screen -XS DMX quit | echo ""'
sleep 5
sudo sh /opt/LibreLight/ASP/netns.sh 25
sudo ip netns exec blue225 su user -c 'screen -d -m -S DMX sh /opt/LibreLight/ASP/start.sh'
#screen -r DMX
#sudo ip netns exec blue224 su user -c 'screen -d -m -S ASP_IN sh /opt/LibreLight/ASP/map14_in_to0.sh'
