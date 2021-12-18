netns=$(ip netns identify $$)
python3 ArtNetProcessor.py netns=$netns
