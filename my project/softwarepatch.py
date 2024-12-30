import os
import requests
import winreg

# Function to fetch the installed software list from the Windows registry
def get_installed_software():
    software_list = {}

    # Registry key for 32-bit and 64-bit installed software
    registry_keys = [r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 
                     r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"]

    try:
        for reg_key in registry_keys:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):  # Loop over all subkeys
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            display_version, _ = winreg.QueryValueEx(subkey, "DisplayVersion")
                            if display_name and display_version:
                                if display_name not in software_list:
                                    software_list[display_name] = []
                                software_list[display_name].append(display_version)
                    except FileNotFoundError:
                        continue
    except Exception as e:
        print(f"Error reading registry: {e}")

    return software_list

# Function to fetch vulnerability details from Vulners API
def get_vulnerability_info_vulners(software_name, version, api_key):
    # Vulners API endpoint for searching vulnerabilities
    api_url = f"https://vulners.com/api/v3/search/lucene/?query={software_name}%20{version}&apiKey={api_key}"

    try:
        # Send the request to the Vulners API
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            # Check if there are any vulnerability results
            if 'data' in data and 'search' in data['data']:
                vulnerabilities = data['data']['search']
                if vulnerabilities:
                    print(f"Found {len(vulnerabilities)} vulnerabilities for {software_name} version {version}.")
                    return vulnerabilities
                else:
                    return None
            else:
                print(f"No vulnerability data available for {software_name} version {version}.")
                return None
        else:
            print(f"Failed to fetch data from Vulners API. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Vulners API: {e}")
    
    return None

# Function to save vulnerabilities to a text file (only those with vulnerabilities)
def save_vulnerabilities_to_file(software_list, vulnerabilities):
    with open("software_vuln.txt", "w") as vuln_file:
        for software, versions in software_list.items():
            for version in versions:
                software_vulnerabilities = vulnerabilities.get(f"{software} {version}", [])
                if software_vulnerabilities:  # Only save software with vulnerabilities
                    for vulnerability in software_vulnerabilities:
                        cve_id = vulnerability.get('id', 'N/A')
                        vuln_file.write(f"Software: {software}, Version: {version}, Vulnerability ID: {cve_id}\n")
                    break  # Save only the first found vulnerability for that version
    print("Vulnerabilities saved to software_vuln.txt")

# Function to collect installed software and check vulnerabilities
def main():
    # Fetch list of installed software from the system registry
    software_list = get_installed_software()

    api_key = "FZ9BDD2TJ533UMPD4RAG8TC2N3KZKJ5RNN4LVNU53YTM6Q4NC3B78GI7FN2Y5AUW"
    vulnerabilities = {}

    for software, versions in software_list.items():
        for version in versions:
            print(f"Checking vulnerabilities for: {software} version {version}")
            vulnerability_info = get_vulnerability_info_vulners(software, version, api_key)
            if vulnerability_info:
                vulnerabilities[f"{software} {version}"] = vulnerability_info
            else:
                vulnerabilities[f"{software} {version}"] = []

    # Save only the vulnerable software versions to a text file
    save_vulnerabilities_to_file(software_list, vulnerabilities)

# Run the script
if __name__ == "__main__":
    main()
