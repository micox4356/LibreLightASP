netns=$(ip netns identify $$)
python3 /opt/LibreLight/ASP/ArtNetProcessor.py netns=$netns
