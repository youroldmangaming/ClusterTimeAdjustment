#check for GPS data
sudo cat /dev/ttyS0

sudo apt-get install chrony





echo "Setup Time Server"
# Configure chrony for time synchronization
RUN echo "server pool.ntp.org iburst" >> /etc/chrony/chrony.conf \
    && echo "allow all" >> /etc/chrony/chrony.conf
service chrony start
chronyc -a makestep
