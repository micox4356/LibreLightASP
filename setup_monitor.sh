#!/usr/bin/bash
user="pi"
user="micha"
ip=17
sudo sh /home/$user/ASP/netns.sh $ip

#sudo ip netns exec blue2$ip su pi -c 'screen -d -m -S ASP_IN sh /home/user/ASP/start.sh'
sudo ip netns exec blue2$ip su $user -c "sh /home/$user/ASP/start.sh"
