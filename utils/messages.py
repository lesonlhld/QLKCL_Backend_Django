SUCCESS = 'Success'
WARNING = 'Warning'
CONTACT_ADMIN_FOR_SUPPORT = 'Contact admin for support'
INVALID_ARGUMENT = 'Invalid argument'
FIELD_NOT_SUPPORT = 'Field is not support'
NO_PERMISSION = 'Permission denied'
NOT_FOUND_EXCEPTION = 'Not found exception'
NETWORK_EXCEPTION = 'Network exception'
VALIDATION_EXCEPTION = 'Validation exception'
DUPLICATE = 'Object is already exist'

EXIST = 'Exist'
NOT_EXIST = 'Not exist'
INVALID = 'Invalid'
WRONG = 'Wrong'
TIME_OUT = 'Time out'
NOT_AVAILABLE = 'Not available'
CANNOT_CHANGE = 'Cannot change'

EMPTY = 'EMPTY'
MUST_EMPTY = 'Must empty'

CANNOT_CONVERT_STRING_TO_INT = 'Cannot convert string to int'
CANNOT_CONVERT_STRING_TO_FLOAT = 'Cannot convert string to float'

CODE_EMPTY = 'Code must not be empty'
NAME_EMPTY = 'Name must not be empty'
ADDRESS_EMPTY = 'Address must not be empty'
PHONE_EMPTY = 'Phone must not be empty'
QUARANTINE_ROOM_EMPTY = 'Quarantine room must not empty'
FILE_IMPORT_EMPTY = 'File import must not be empty'

CODE_NOT_FOUND = 'Code is not exist'
USER_NOT_FOUND = 'User is not exist'
MEMBER_NOT_FOUND = 'Member is not exist'
TEST_NOT_FOUND = 'Test is not exist'
COUNTRY_NOT_FOUND = 'Country code is not exist'
CITY_NOT_FOUND = 'City code is not exist'
DISTRICT_NOT_FOUND = 'District code is not exist'
WARD_NOT_FOUND = 'Ward code is not exist'
QUARANTINE_WARD_NOT_FOUND = 'Quarantine Ward is not exist'
QUARANTINE_BUILDING_NOT_FOUND = 'Quarantine Building is not exist'
QUARANTINE_FLOOR_NOT_FOUND = 'Quarantine Floor is not exist'
QUARANTINE_ROOM_NOT_FOUND = 'Quarantine Room is not exist'
NOTIFICATION_NOT_FOUND = 'Notification is not exist'
USER_NOTIFICATION_NOT_FOUND = 'User Notification is not exist'

CODE_EXIST = 'Code is already exist'

INVALID_POSITIVE_FLOAT = 'Value must be positive float'
INVALID_PHONE_NUMBER = 'Invalid phone number'
INVALID_DATETIME = r"""Invalid datetime field, must be vd:'2000-01-26T01:23:45.123456Z'"""

QUARANTINE_ROOM_FULL = 'Full'
UPDATED_CAPACITY_SMALLER_THAN_MEMBER = 'Updated capacity is smaller than number of current member'

# password
TOO_SHORT = 'TOO_SHORT'
ENTIRELY_NUMERIC = 'ENTIRELY_NUMERIC'
MUST_CONTAIN_NUMBER = 'MUST_CONTAIN_NUMBER'
MUST_CONTAIN_UPPERCASE_CHARACTERS = 'MUST_CONTAIN_UPPERCASE_CHARACTERS'
MUST_CONTAIN_SPECIAL_CHARACTERS = 'MUST_CONTAIN_SPECIAL_CHARACTERS'
INVALID_POSITIVE_INTEGER = 'Value must be positive integer'
DUPLICATE_NEW_PASSWORD = 'New password is the same with old password'
CONFIRM_PASSWORD_NOT_MATCH = 'Confirm password is not match'
WRONG_PASSWORD = 'Wrong password'
INVALID_OTP = 'Invalid OTP'

INVALID_STATUS = 'Invalid status'
INVALID_TYPE = 'Invalid type'
INVALID_QUARANTINE_TIME = 'Quarantine time must be positive float'
INVALID_CAPACITY_NUMBER = 'Capacity number must be positive integer'
INVALID_IS_FULL_FIELD = 'is_full must be boolean type'
INVALID_ROOM_QUANTITY = 'Room quantity must be positive integer'
INVALID_ROLE_ID = 'Role ID is invalid'

# paging
NEGATIVE_PAGE = 'Page must be positive integer'
NEGATIVE_PAGE_SIZE = 'Page size must be positive integer'
OVER_PAGE_SIZE_MAX = 'Page size must not be greater than '

ISNOTMEMBER = 'This user is not a member'
ISNOTMANAGER = 'This user is not a manager'
ISNOTSTAFF = 'This user is not a staff'
ISNOTWAITING = 'This user is not waiting'
ISNOTAVAILABLE = 'This user is not available'
ISNOTLEAVE = 'This user is not leave'
IS_NOT_WAITING_OR_REFUSED = 'This user is not waiting or refused'
IS_NOT_AVAILABLE_OR_LEAVE = 'This user is not available or leave'
CANNOT_FINISH_QUARANTINE = 'This member cannot finish quarantine'

NOT_IN_QUARANTINE_WARD_OF_MEMBER = r"""Not in the quarantine ward of this member"""

CANNOT_CHANGE_ROOM_LABEL_TOGETHER = 'Cannot change room and label together'

# quarantine history
PRESENT_QUARANTINE_HISTORY_EXIST = 'PRESENT quarantine history exist'
PRESENT_QUARANTINE_HISTORY_NOT_EXIST = 'PRESENT quarantine history not exist'
MANY_PRESENT_QUARANTINE_HISTORY_EXIST = 'Many PRESENT quarantine history exist'

# hospitalize
CANNOT_HOSPITALIZE_THIS_HOSPITAL = 'Cannot hospitalize to this hospital'
IS_NOT_HOSPITALIZE_WAITING = 'This member is not hospitalize waiting'
ALREADY_HOSPITALIZE_WAITING = 'This member is already hospitalize waiting'