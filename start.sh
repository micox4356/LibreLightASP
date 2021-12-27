netns=$(ip netns identify $$)
python3 ~/ASP/ArtNetProcessor.py netns=$netns
