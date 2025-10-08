import sys
import json
import re


def generate_removeowner_command(disk_output):
    removeowner_disks = []

    # disk_output is a list of lines, not a string
    data_started = False
    for line in disk_output:
        line = line.strip()
        if not line:
            continue
        # Skip header and separator lines
        if 'Usable' in line or ('Disk' in line and 'Size' in line):
            continue
        if line == '--':
            data_started = True
            continue
        if 'entries were displayed' in line:
            break
        if data_started:
            parts = line.split()
            # Check if disk is unassigned (column 6)
            if len(parts) >= 6 and parts[5] == "unassigned":
                disk_name = parts[0]
                removeowner_disks.append(disk_name)

    removeowner_cmd = "storage disk removeowner " + ", ".join(removeowner_disks) if removeowner_disks else ""
    return removeowner_cmd

if __name__ == "__main__":
    # Read JSON data from stdin
    disk_show_data = json.load(sys.stdin)

    # Generate removeowner command
    removeowner_cmd = generate_removeowner_command(disk_show_data)
    print("Generated Command:")
    if removeowner_cmd:
        print(removeowner_cmd)




