
import serial
import time
import re

CONNECTION_TIME = 2
CONNECTION_PORT = 'COM5'


class ScaleManager:

    @staticmethod
    def get_value():
        try:
            connection = serial.Serial(CONNECTION_PORT)
            if connection.name == CONNECTION_PORT:
                counter = 0
                while counter <= CONNECTION_TIME:
                    data = connection.readline()
                    tag_re = re.compile(r'[-+]?([0-9]*(\,|\.)[0-9]+|[0-9]+)', re.MULTILINE)
                    matches = tag_re.findall(data)
                    if matches:
                        connection.close()
                        return matches[0]
                    time.sleep(0.1)
                    counter += 0.1
            connection.close()
            return False
        except Exception as e:
            return False
