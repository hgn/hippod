import datetime



def string_to_datetime(date_string):
	date_time = datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%f')
	return date_time