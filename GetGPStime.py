import time
import argparse
from datetime import datetime, timedelta
import serial  # Ensure you have pyserial installed for serial communication
import subprocess  # To run shell commands

# Replace '/dev/ttyS0' with your serial port
serial_port = '/dev/ttyS0'
baud_rate = 9600  # Set the baud rate according to your device specifications

# Function to determine if DST is in effect
def is_dst(dt):
    """Check if Daylight Saving Time is in effect."""
    last_sunday_september = dt.replace(month=9, day=1) + timedelta(days=30)
    last_sunday_september -= timedelta(days=last_sunday_september.weekday() + 1)

    first_sunday_april = dt.replace(month=4, day=1) + timedelta(days=(7 - dt.replace(month=4, day=1).weekday()) % 7)

    return last_sunday_september <= dt > first_sunday_april

def parse_gps_data(data):
    """Parse latitude and longitude from GPS data."""
    try:
        parts = data.split(',')
        lat = parts[2]
        lat_dir = parts[3]
        lon = parts[4]
        lon_dir = parts[5]

        lat = float(lat[:-2]) + (float(lat[-2:]) / 60.0) if lat_dir == 'N' else - (float(lat[:-2]) + (float(lat[-2:]) / 60.0))
        lon = float(lon[:-2]) + (float(lon[-2:]) / 60.0) if lon_dir == 'E' else - (float(lon[:-2]) + (float(lon[-2:]) / 60.0))

        return lat, lon
    except (IndexError, ValueError) as e:
        print(f"Error parsing GPS data: {e}")
        return None, None

def update_os_time(local_time):
    """Update the OS time using the provided local time."""
    command = f'date -s "{local_time}"'
    subprocess.run(command, shell=True)

def main(update_interval):
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
                            utc_time = datetime.strptime(utc_time_str, '%H%M%S.%f')
                            day = int(date_str[0:2])
                            month = int(date_str[2:4])
                            year = 2000 + int(date_str[4:6])

                            utc_time = utc_time.replace(year=year, month=month, day=day)

                            # Check if DST is in effect
                        #    if is_dst(utc_time):
                        #        utc_time += timedelta(hours=13)  # Adjust for UTS+DST 
                        #    else:
                        #       utc_time += timedelta(hours=12)  # Adjust for UTS, NZ is UTS+12. I could use LAT/LON to determine this later

                            local_time = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

                            print(f'Local Time (with DST adjustment): {local_time}')

                            # Update OS time
                            update_os_time(local_time)

                            # Wait for specified interval before the next update
                            time.sleep(update_interval)

                    # Check for GPGGA sentences to get latitude and longitude
                    if data.startswith('$GPGGA'):
                        lat, lon = parse_gps_data(data)
                        print(f'Latitude: {lat}, Longitude: {lon}')

    except serial.SerialException as e:
        print(f'Error: {e}')
    except KeyboardInterrupt:
        print('Program terminated by user')

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='GPS Time Synchronization')
    parser.add_argument('--update-interval', type=int, default=3600,
                        help='Update interval in seconds (default: 3600 seconds)')
    
    args = parser.parse_args()
    
    # Call main function with the update interval
    main(args.update_interval)
