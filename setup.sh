#check for GPS data
sudo cat /dev/ttyS0

sudo apt-get install chrony
sudo apt install gpsd gpsd-clients


echo "USBAUTO="true"
START_GPSD="true"
GPSD_OPTIONS="-n"
DEVICES="/dev/ttyS0"
" > /etc/default/gpsd 


echo "refclock SHM 0 refid GPS stratum 10
refclock SHM 0 refid GPS precision 1e-1 offset 0.5 delay 0.2
confdir /etc/chrony/conf.d
sourcedir /etc/chrony/sources.d
keyfile /etc/chrony/chrony.keys
driftfile /var/lib/chrony/chrony.drift
ntsdumpdir /var/lib/chrony
logdir /var/log/chrony
maxupdateskew 100.0
rtcsync
makestep 1 3
leapsectz right/UTC
local stratum 8
allow 192.168.188.0/24
" >/etc/chrony/chrony.conf

sudo systemctl enable chrony
sudo systemctl start chrony

sudo systemctl enable gpsd
sudo systemctl start gpsd

chronyc sources
chronyc tracking
