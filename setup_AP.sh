#ip l add link br0 type bridge

#ip netns add ap2 66
#iw phy wlan0 set netns ap2
#iw phy wlan0 set netns 66
#ip l set wlan0 netns 66
sleep 1
date

killall hostapd
killall wpa_supplicant
killall dnsmasq
sleep 1
ip l set wlan0 up

sleep 2
rfkill unblock all
ip l set wlan0 up
sleep 2
ip a add 192.168.4.11/24 dev wlan0

#for internet routing
#iptables -t nat -A POSTROUTING -m iprange --src-range 192.168.4.0-192.168.4.255 -o eth0 -j MASQUERADE


#-B in background
#/usr/sbin/hostapd -B -P /run/hostapd.pid /etc/hostapd/hostapd.conf
/usr/sbin/hostapd -B -P /run/hostapd.pid hostapd.conf
sleep 2

# -q debugg -d no-deamon
/usr/sbin/dnsmasq  --dhcp-range=192.168.4.100,192.168.4.110 -q -a 192.168.4.11
date
echo "ende ----------------"
#read -p hi
#sleep 9999

