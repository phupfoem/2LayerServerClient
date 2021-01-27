from datetime import datetime


def print_msg(msg):
    current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('[' + str(current_date_time) + '] ' + msg)
