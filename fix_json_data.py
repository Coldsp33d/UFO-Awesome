# `python3.6 fix_json_data.py`

# Run this program once to fix malformed JSON data. 
# It should then be possible to use pandas' JSON parser library to load the data

import json
import re

import fileinput

count = 0
for i, line in enumerate(fileinput.input('Data/ufo_awesome.json', inplace=True)):
    try:
        data = json.loads(line)

    except ValueError:
        count += 1
        data = json.loads(
                    re.sub(r'\\+(?!")', r'\\\\', 
                        re.sub(r'(?<=\s")(.*?)(?="[,:] ")', lambda x: x.group(1).replace('"', r'\\"'), line)
                    )
                )

    print(json.dumps(data))

print(f"{count} Records modified.")



