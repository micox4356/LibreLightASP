sleep 10
sudo sh /opt/LibreLight/ASP/netns.sh 23
sudo ip netns exec blue223 su user -c 'screen -d -m -S oszi sh /opt/LibreLight/ASP/monitor/loop_oszi.sh'

