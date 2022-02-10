#!/usr/bin/sh

while :
do
  sh '/opt/LibreLight/ASP/start.sh'
  PS1="X:"
  PS1="$PS1 $(ip netns identify $$)"
  export PS1
  echo "execute some command or, exit shell and restart loop with <CTRL+D>"
  sh
  echo "Press <CTRL+C> to exit. in 1sec to exit screen loop"
  sleep 5
done

