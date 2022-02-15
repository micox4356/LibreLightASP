#copy this dir ASP/netns to /opt/ as root 
cp -r ../netns /opt/
chown -R root:root /opt/netns

# add with sudo visudo
echo "insert into visudo"
echo "user      ALL=(ALL) NOPASSWD:/opt/netns/_exec, /opt/netns/create"

read tmp
visudo

# now "user" can create "ip netns" with
#sudo /opt/netns/create 14

# and attache as "user" any cmd to it with
#/opt/netns/exec --id=14 --cmd=bash
