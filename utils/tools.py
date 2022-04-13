import re
import datetime
import os
from random import randint
import pytz
import math, random
from .enums import MemberLabel

def split_input_list(str_list):
    """
    Separate out individual student email from the comma, or space separated string.
    e.g.
    in: "Lorem@ipsum.dolor, sit@amet.consectetur\nadipiscing@elit.Aenean\r convallis@at.lacus\r, ut@lacinia.Sed"
    out: ['Lorem@ipsum.dolor', 'sit@amet.consectetur', 'adipiscing@elit.Aenean', 'convallis@at.lacus', 'ut@lacinia.Sed']
    `str_list` is a string coming from an input text area
    returns a list of separated values
    """

    if str_list == None:
        return []

    new_list = re.split(r'[\n\r,]', str_list)

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

def is_change_date_in_time_zone_vn(datetime1, datetime2):
    """
    input must be datetime with timezone
    """

    if datetime1 and not datetime2:
        return True
    elif not datetime1 and datetime2:
        return True
    elif not datetime1 and not datetime2:
        return False
    else:
        vntz = pytz.timezone('Asia/Saigon')

        datetime1_vntz = datetime1.astimezone(vntz)
        datetime2_vntz = datetime2.astimezone(vntz)

        return not (datetime1_vntz.year == datetime2_vntz.year and datetime1_vntz.month == datetime2_vntz.month and datetime1_vntz.day == datetime2_vntz.day)

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

def generateOTP(number_of_digits):
    
    digits = "0123456789"
    otp = ""
    for i in range(number_of_digits):
        otp += digits[math.floor(random.random() * 10)]
    
    return otp

def custom_user_code_generator(quarantine_ward_id):
    first_part_length = int(os.environ.get("USER_CODE_QUARANTINE_WARD_ID_LENGTH", "3"))
    first_part = ('0000000000' + str(quarantine_ward_id))[-first_part_length:]
    
    second_part_length = int(os.environ.get("USER_CODE_TIMESTAMP_LENGTH", "6"))
    second_part = ('0000000000' + str(int(datetime.datetime.now().timestamp())))[-second_part_length:]

    third_part_length = int(os.environ.get("USER_CODE_RANDOM_LENGTH", "6"))
    third_part = ''.join(str(randint(0, 9)) for i in range(third_part_length))

    return first_part + second_part + third_part

def get_key_from_value_in_dict(dict, value):
    return list(dict.keys())[list(dict.values()).index(value)]

class LabelTool:
    label_value_dict = {
        MemberLabel.F0 : 0,
        MemberLabel.F1 : 1,
        MemberLabel.F2 : 2,
        MemberLabel.F3 : 3,
        MemberLabel.FROM_EPIDEMIC_AREA : 4,
        MemberLabel.ABROAD : 5,
    }

    def get_value_of_label(self, label):
        return self.label_value_dict[label]

    def is_F_label(self, label):
        if 0 <= self.get_value_of_label(label) <= 3:
            return True
        else:
            return False

    def compare_label(self, label1, label2):
        """
        label1 serious more than label2: return 1
        label1 serious same than label2: return 0
        label1 serious less than label2: return -1
        """
        if self.get_value_of_label(label1) < self.get_value_of_label(label2): return 1
        if self.get_value_of_label(label1) == self.get_value_of_label(label2): return 0
        if self.get_value_of_label(label1) > self.get_value_of_label(label2): return -1

    def down_label(self, label):
        """
        return label that less serious than input label one level
        """
        try:
            new_label_value = self.get_value_of_label(label) + 1
            return get_key_from_value_in_dict(self.label_value_dict, new_label_value)
        except Exception as exception:
            return label
