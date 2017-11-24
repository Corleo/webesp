'''
Inspection script for debugging measurement data and transmitted / received data.
'''

# '''
import os
import sys

# DIR_PATH = os.path.expanduser("~/projetos/webapp/app/_bokeh/models/")
# sys.path.append(DIR_PATH)

sys.path.append("../webapp/app/_bokeh/models/")

import re
import util
import json


t_raw_old = 0
t_old     = 0
raw_data  = []
new_data  = dict(f=[], t=[])


with open('data_dump.txt', 'r') as file:
    for line in file:
        line = line.rstrip('\n')
        line = re.search("(\[[0-9.,\s]+\])\)$", line).group(1)

        raw_data += json.loads(line)

with open('data_processed.txt', 'w') as file:
    for _index, _value in enumerate(raw_data):
        # raw_data = [<time>,<force>,<time>,<force>,...]
        if _index % 2 == 1: continue

        try:
            _new_f = float(raw_data[_index+1]) * 0.1558617100780375
            t_raw_new = raw_data[_index]

            if t_raw_old == 0:
                _new_t = 0
            else:
                # _new_t = t_old + t_raw_new - t_raw_old
                _new_t = t_old + util.esp_time_diff(t_raw_new, t_raw_old)

            t_raw_old = t_raw_new
            t_old = _new_t

            new_data['f'].append(_new_f)
            new_data['t'].append(float(_new_t) * 1e-6)

            # print('f: %7.3f | t: %7.3f | f_raw: %5d | t_raw: %11d' % (
            #         new_data['f'][-1],
            #         new_data['t'][-1],
            #         raw_data[_index+1],
            #         raw_data[_index],
            #     )
            # )

            file.write("f: %7.3f | t: %7.3f | f_raw: %5d | t_raw: %11d\n" % (
                    new_data['f'][-1],
                    new_data['t'][-1],
                    raw_data[_index+1],
                    raw_data[_index],
                )
            )

        except Exception as e:
            print("Exception in processing measures: {}".format(e))
            print("Data in Exception: {}".format(raw_data))


print "new_data['t'] len:", len(new_data['t'])
print ''
# '''
