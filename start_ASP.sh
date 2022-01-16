echo "sleep 5"
#sleep 5
netns=$(ip netns identify $$)


python3 /home/pi/ASP/ArtNetProcessor.py --recive 10. --sendto 2.255.255.255 netns=$netns
if [ $? != 0 ]; then
     python3 /home/user/ASP/ArtNetProcessor.py --recive 10. --sendto 2.255.255.255 netns=$netns
     #python3 /home/micha/ASP/ArtNetProcessor.py --recive 10. --sendto 2.255.255.255 netns=$netns
  
fi
