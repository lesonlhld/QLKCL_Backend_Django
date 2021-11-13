import re
import datetime
from datetime import time, timezone
import pytz

def split_input_list(str_list):
    """
    Separate out individual student email from the comma, or space separated string.
    e.g.
    in: "Lorem@ipsum.dolor, sit@amet.consectetur\nadipiscing@elit.Aenean\r convallis@at.lacus\r, ut@lacinia.Sed"
    out: ['Lorem@ipsum.dolor', 'sit@amet.consectetur', 'adipiscing@elit.Aenean', 'convallis@at.lacus', 'ut@lacinia.Sed']
    `str_list` is a string coming from an input text area
    returns a list of separated values
    """

    new_list = re.split(r'[\n\r\s,]', str_list)

    new_list = [s.strip() for s in new_list]

    new_list = [s for s in new_list if s != '']

    return new_list

def date_string_to_timestamp(date, add_day=0):
    newday = datetime.datetime.strptime(date, '%d/%m/%Y')

    newday += datetime.timedelta(days=add_day)

    day = ('0' + str(newday.day))[-2:]
    month = ('0' + str(newday.month))[-2:]
    year = ('000' + str(newday.year))[-4:]
    return f'{year}-{month}-{day} 00:00:00+07'

def timestamp_string_to_date_string(timestamp_string):
    # from '2000-01-02 00:00:00+07' to '02/01/2000'
    timestamp_string = str(timestamp_string)
    return timestamp_string[8:10] + '/' + timestamp_string[5:7] + '/' + timestamp_string[0:4]

def compare_date_string(date1, date2):
    # date: 'dd/mm/yy'
    # date1 < date2 return -1
    # date1 = date2 return 0
    # date1 > date2 return 1
    year1 = int(date1[-4:])
    year2 = int(date2[-4:])
    if year1 < year2:
        return -1
    elif year1 > year2:
        return 1
    else:
        month1 = int(date1[3:5])
        month2 = int(date2[3:5])
        if month1 < month2:
            return -1
        elif month1 > month2:
            return 1
        else:
            day1 = int(date1[:2])
            day2 = int(date2[:2])
            if day1 < day2:
                return -1
            elif day1 > day2:
                return 1
            else:
                return 0

def room_to_quarantine_ward(room):
    """
    Now not use
    From room, return a dict of quarantine_ward, quarantine_building, quarantine_floor, quarantine_room
    """

    floor = room.quarantine_floor
    building = floor.quarantine_building
    quarantine_ward = building.quarantine_ward

    return {
        'quarantine_ward': quarantine_ward,
        'quarantine_building': building,
        'quarantine_floor': floor,
        'quarantine_room': room,
    }