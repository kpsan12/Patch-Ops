import re

# Open and read the input file
try:
    with open('software_vuln.txt', 'r') as infile:
        lines = infile.readlines()
except FileNotFoundError:
    print("Error: 'input.txt' not found. Please ensure the file exists in the same directory as the script.")
    exit()

# Open the output file for writing
with open('softwarevulnresults.txt', 'w') as outfile:
    found_any_vulnerabilities = False  # Track if any vulnerabilities were found

    for line in lines:
        # Check if the line contains '<number> Vulnerabilities Found'
        match = re.search(r'(\d+)\s+Vulnerabilities Found', line)
        if match:
            # Extract software name and version from the line
            software_line = line.split(",")[0]  # Assuming Software and Version are before the first comma
            outfile.write(software_line.strip() + '\n')
            found_any_vulnerabilities = True

    if not found_any_vulnerabilities:
        print("No vulnerabilities found in the input file.")

print("Filtered results have been written to 'softwarevulnresults.txt'.")
