#!/usr/bin/env python3

import sys

file_path = "/etc/nixos/configuration.nix"

def add_package_to_nix_config(package_name):
    try:
        # Read the file content
        with open(file_path, "r") as file:
            lines = file.readlines()
        
        # Find the line and insert the package after it
        for i, line in enumerate(lines):
            if 'environment.systemPackages = with pkgs; [' in line:
                lines.insert(i + 1, f"  {package_name} # added by nstall\n")
                break
        
        # Write the modified content back to the file
        with open(file_path, "w") as file:
            file.writelines(lines)
        
        print(f"Successfully added '{package_name}' to {file_path}")
    
    except Exception as e:
        print(f"Error: {e}")

def remove_package_from_nix_config(package_name):
    in_system_packages_block = False

    try:
        # Read the file content
        with open(file_path, "r") as file:
            lines = file.readlines()
        
        # Filter out the specified package between the systemPackages block
        for i, line in enumerate(lines):
            if 'environment.systemPackages = with pkgs; [' in line:
                in_system_packages_block = True  # Start tracking block
                continue
            elif '];' in line and in_system_packages_block:
                in_system_packages_block = False  # End of block, stop tracking
                break
            elif in_system_packages_block:
                if package_name in line:
                    print(f"Removing '{package_name}' from {file_path}")
                    lines[i] = ''  # Remove the line containing the package
        
        # Write the modified content back to the file
        with open(file_path, "w") as file:
            file.writelines(lines)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: sudo nstall <add/remove> <package_name>")
    else:
        action = sys.argv[1].lower()
        package_name = sys.argv[2]

        if action == "install" or action == "add":
            add_package_to_nix_config(package_name)
        elif action == "remove":
            remove_package_from_nix_config(package_name)
        else:
            print("nstall: Invalid action. Use 'add' or 'remove'.")
