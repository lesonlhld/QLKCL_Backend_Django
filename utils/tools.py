import re

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