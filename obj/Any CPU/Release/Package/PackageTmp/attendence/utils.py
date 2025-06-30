from datetime import datetime

def calculate_status(check_in, settings):
    check_in_time = datetime.combine(datetime.today(), settings.check_in_time)
    actual = datetime.combine(datetime.today(), check_in)
    diff = (actual - check_in_time).total_seconds() / 60
    if diff <= settings.grace_period:
        return 'Present'
    elif diff <= settings.late_threshold:
        return 'Late'
    else:
        return 'Absent'
