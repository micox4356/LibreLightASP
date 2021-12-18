nr="2$1"
echo $1
#exit 
ip netns del "blue$nr"
ip l del veth0$nr

ip netns add "blue$nr"
ip netns list
#ip link add veth0$nr type veth peer name veth1$nr
ip link add veth0$nr type veth peer name veth1$nr netns "blue$nr"
ip link set dev veth0$nr up
ip netns exec "blue$nr" ip link set dev veth1$nr up
ip link set veth0$nr master br0
ip link list
#ip link set veth1$nr netns "blue$nr"

ip netns exec "blue$nr" ip addr add 10.10.10.$nr/24 dev veth1$nr
ip netns exec "blue$nr" ip addr add 10.0.25.$nr/24 dev veth1$nr
ip netns exec "blue$nr" ip addr add 2.0.0.$nr/8 dev veth1$nr:1
#ip netns exec "blue$nr" 'su - user' 
ip netns exec "blue$nr" su - user
