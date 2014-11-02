Want to use ir blasting with XBMC/Kodi on OpenELEC and found out eventlircd does not support it?
XBMC/Kodi only supports 1 lirc socket, so you had two options:
- Write a (python) script to send commands to your seperate lircd 
  on a raspberry pi this worked incredibly slow for me:
  python takes 1-2 seconds to start up which is ok for just powering on a device but for volume control it is completely useless.
  Running shell scripts was pretty slow too, XBMC/Kodi forks for every script
- Replace eventlircd with lircd
  This required more work and configuring than I would like but ir blasting works fast with just LIRC.Send().

So I opted for the third option:
- Write some code that listens on one socket and forwards messages from eventlircd and sends ir blaster commands to lircd.

./lircsocket.py -h
usage: lircsocket.py [-h] [-e EVENTLIRCD] [-l LIRCD] [-s SOCKET] [-v] [-d]

interconnect eventlircd and lircd to get lircd (ir blasting) and eventlircd to
work over a single socket.

optional arguments:
  -h, --help            show this help message and exit
  -e EVENTLIRCD, --eventlircd EVENTLIRCD
                        socket for eventlircd
  -l LIRCD, --lircd LIRCD
                        socket for lircd
  -s SOCKET, --socket SOCKET
                        listening socket for me
  -v, --verbose         be a bit verbose
  -d, --debug           debug communication

  
