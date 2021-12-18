netns=$(ip netns identify $$)
python3 ArtNetProcessor.py -s 10.10.10.255 -r 2.0.0.14 --inmap 1 netns=$netns
