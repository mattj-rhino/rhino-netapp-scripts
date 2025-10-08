import sys
import json
import re

def parse_netapp_disk_output(lines):
    """
    Parse NetApp 'disk show' command output.

    Returns a list of dictionaries with disk information.
    """
    disks = []
    # Skip header lines and separator lines
    # Data starts after the '--' separator
    data_started = False

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Skip header lines (contain 'Usable', 'Disk', 'Container')
        if 'Usable' in line or ('Disk' in line and 'Size' in line):
            continue

        # Mark that we've seen the separator
        if line.strip() == '--':
            data_started = True
            continue

        # Stop at summary line
        if 'entries were displayed' in line:
            break

        # Parse data lines (after separator)
        if data_started:
            # Use regex to match the pattern more precisely
            # Format: DiskName Size Shelf Bay DiskType ContainerType [ContainerName Owner]
            # Split on whitespace, handling the variable spacing
            parts = line.split()

            if len(parts) >= 6:
                # Basic parsing - adjust indices based on actual columns
                disk_name = parts[0]
                size = parts[1]
                shelf = parts[2]
                bay = parts[3]
                disk_type = parts[4]
                container_type = parts[5]
                container_name = parts[6] if len(parts) > 6 else '-'
                owner = parts[7] if len(parts) > 7 else '-'

                disk_info = {
                    'disk': disk_name,
                    'size': size,
                    'shelf': shelf,
                    'bay': bay,
                    'type': disk_type,
                    'container_type': container_type,
                    'name': container_name,
                    'owner': owner,
                    'is_unassigned': container_type == 'unassigned'
                }
                disks.append(disk_info)

    return disks

if __name__ == "__main__":
    # Read JSON data from stdin
    disk_show_data = json.load(sys.stdin)

    # Parse the disk output
    disks = parse_netapp_disk_output(disk_show_data)

    print(f"\n{'='*80}")
    print(f"Total disks found: {len(disks)}")
    print(f"{'='*80}\n")

    # Count unassigned vs assigned
    unassigned = [d for d in disks if d['is_unassigned']]
    assigned = [d for d in disks if not d['is_unassigned']]

    print(f"Assigned disks: {len(assigned)}")
    print(f"Unassigned disks: {len(unassigned)}")
    print()

    # Show unassigned disks
    if unassigned:
        print("Unassigned Disks:")
        print("-" * 80)
        for disk in unassigned:
            print(f" {disk['disk']:20} | Bay: {disk['bay']:3} | Type: {disk['type']}")
        print()

    # Show assigned disks grouped by aggregate
    if assigned:
        print("Assigned Disks:")
        print("-" * 80)
        aggregates = {}
        for disk in assigned:
            agg = disk['name']
            if agg not in aggregates:
                aggregates[agg] = []
            aggregates[agg].append(disk)

        for agg_name, agg_disks in aggregates.items():
            print(f"\n Aggregate: {agg_name} ({len(agg_disks)} disks)")
            for disk in agg_disks:
                print(f" {disk['disk']:20} | Size: {disk['size']:8} | Owner: {disk['owner']}")

    print(f"\n{'='*80}")