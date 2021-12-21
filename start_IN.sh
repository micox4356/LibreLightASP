#sudo /home/pi/ASP/netns.sh 04
#sudo sh /home/user/ASP/netns.sh 04 
netns=$(ip netns identify $$)
#ip netns exec blue204 "su - user bash; cd ASP; 
python3 ArtNetProcessor.py -s 10.10.10.255 -r 2.0.0.14 --inmap 1 netns=$netns
