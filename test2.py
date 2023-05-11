from datetime import datetime
import pytz

time = '2023-05-07T06:55:00.000Z'
time = time.replace('T', ' ').replace('Z', '')
date_format = '%Y-%m-%d %H:%M:%S.%f'
utc = datetime.strptime(time, date_format)
print(utc)