                                                                                                                                                                                                                              gps.py                                                                                                                                                                                                                                          import time
from datetime import datetime, timedelta
import serial  # Ensure you have pyserial installed for serial communication

# Replace '/dev/ttyS0' with your serial port
serial_port = '/dev/ttyS0'
baud_rate = 9600  # Set the baud rate according to your device specifications




# Function to determine if DST is in effect
def is_dst(dt):
    """Check if Daylight Saving Time is in effect."""
    # Get the last Sunday in September
    last_sunday_september = dt.replace(month=9, day=1) + timedelta(days=30)
    last_sunday_september -= timedelta(days=last_sunday_september.weekday() + 1)  # Find last Sunday

    # Get the first Sunday in April
    first_sunday_april = dt.replace(month=4, day=1) + timedelta(days=(7 - dt.replace(month=4, day=1).weekday()) % 7)

    # Check if the date is within the DST range
    return last_sunday_september <= dt > first_sunday_april




def parse_gps_data(data):
    """Parse latitude and longitude from GPS data."""
    parts = data.split(',')
    lat = parts[2]
    lat_dir = parts[3]
    lon = parts[4]
    lon_dir = parts[5]

    if lat_dir == 'S':
        lat = -float(lat[:-2]) - (float(lat[-2:]) / 60.0)
    else:
        lat = float(lat[:-2]) + (float(lat[-2:]) / 60.0)

    if lon_dir == 'W':
        lon = -float(lon[:-2]) - (float(lon[-2:]) / 60.0)
    else:
        lon = float(lon[:-2]) + (float(lon[-2:]) / 60.0)

    return lat, lon

try:
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        print(f'Connected to {serial_port}')
        time.sleep(2)  # Wait for the connection to stabilize

        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').rstrip()
                print(f'Received: {data}')

                # Check for GPRMC sentences for time and date
                if data.startswith('$GPRMC'):
                    parts = data.split(',')
                    utc_time_str = parts[1]
                    date_str = parts[9]  # Get the date from the GPRMC sentence
                    if utc_time_str and date_str:
                        # Convert UTC time to a datetime object
                        utc_time = datetime.strptime(utc_time_str, '%H%M%S.%f')
                        # Construct the full date
                        day = int(date_str[0:2])
                        month = int(date_str[2:4])
                        year = 2000 + int(date_str[4:6])  # Assuming year is in 2000s
                        utc_time = utc_time.replace(year=year, month=month, day=day)


                        print(is_dst(utc_time))



                        # Check if DST is in effect
                        if is_dst(utc_time):
                            utc_time += timedelta(hours=1)  # Adjust for DST

                        local_time = utc_time.strftime("%Y-%m-%d %H:%M:%S")
                        print(f'Local Time (with DST adjustment): {local_time}')

                # Check for GPGGA sentences to get latitude and longitude
                if data.startswith('$GPGGA'):
                    lat, lon = parse_gps_data(data)
                    print(f'Latitude: {lat}, Longitude: {lon}')

except serial.SerialException as e:
    print(f'Error: {e}')
except KeyboardInterrupt:
    print('Program terminated by user')


































^G Help            ^O Write Out       ^W Where Is        ^K Cut             ^T Execute         ^C Location        M-U Undo           M-A Set Mark       M-] To Bracket     M-Q Previous       ^B Back            ^◂ Prev Word       ^A Home            ^P Prev Line       M-▴ Scroll Up      ^▴ Prev Block      M-( Begin of Paragr^Y Prev Page       M-\ First Line     M-◂ Prev File      ^I Tab             ^H Backspace       M-Bsp Chop Left    M-T Cut Till End   M-D Word Count
^X Exit            ^R Read File       ^\ Replace         ^U Paste           ^J Justify         ^/ Go To Line      M-E Redo           M-6 Copy           ^Q Where Was       M-W Next           ^F Forward         ^▸ Next Word       ^E End             ^N Next Line       M-▾ Scroll Down    ^▾ Next Block      M-) End of Paragrap^V Next Page       M-/ Last Line      M-▸ Next File      ^M Enter           ^D Delete          ^Del Chop Right    M-J Full Justify   M-V Verbatim
