echo "sleep 5"
#sleep 5
path="/opt/LibreLight"
netns=$(ip netns identify $$)

python3 $path/ASP/ArtNetProcessor.py --recive 10. --sendto 2.255.255.255 netns=$netns
