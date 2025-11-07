#!/usr/bin/env python
import re
import sys

filename = sys.argv[1]
with open(filename, "r") as inf:
    content = inf.readlines()

reg = re.match(r'# number_of_header_lines: (\d+)\n', content[0])
num_hea = int(reg.group(1))
header = content[:num_hea]

i = 1
prev = None
ouf = None
for line in content[num_hea:]:
    check = line.split()[-6:-1]
    if prev is None or prev != check:
        if ouf:
            ouf.close()
        ouf = open(filename + str(i), "w")
        ouf.writelines(header)
        prev = check
        i += 1
    ouf.write(line)
if ouf:
    ouf.close()

