#!/usr/bin/env python3

import sys
import subprocess
import os
import toml

# Replace later with actual way to select a directory and a file (or at least a directory!)
dir_path = "/etc/nixos"
file_path = f"{dir_path}/configuration.nix"


def add_package_to_nix_config(package_name):
    defaultToml = {"packages": {"nixpkgs": {"pks": []}}}
    tomlFile = f"{dir_path}/configuration.toml"
    if not os.path.isfile(tomlFile):
        with open(tomlFile, "w") as f:
            toml.dump(defaultToml, f)
    try:
        # Read the file content
        with open(f"{dir_path}/configuration.toml", "r") as file:
            config = toml.load(file)
            config['packages']['nixpkgs']['pks'].append(package_name)
        with open(f"{dir_path}/configuration.toml", "w") as file:
            toml.dump(config, file)
    except Exception as e:
        print(f"Error: {e}")


def remove_package_from_nix_config(package_name):
    in_system_packages_block = False
    try:
        # Read the file content
        with open(f"{dir_path}/configuration.toml", "r") as file:
            lines = file.readlines()

        # Filter out the specified package between the systemPackages block
        for i, line in enumerate(lines):
            if "environment.systemPackages = with pkgs; [" in line:
                in_system_packages_block = True  # Start tracking block
                continue
            elif "];" in line and in_system_packages_block:
                in_system_packages_block = False  # End of block, stop tracking
                break
            elif in_system_packages_block:
                if package_name in line:
                    print(f"Removing '{package_name}' from {file_path}")
                    lines[i] = ""  # Remove the line containing the package

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
        rebuild = False

        if action == "install" or action == "add":
            try:
                add_package_to_nix_config(package_name)
                rebuild = True
            except Exception as e:
                print(e)
            # Run a nixos-rebuild
        elif action == "remove":
            try:
                remove_package_from_nix_config(package_name)
                rebuild = True
            except Exception as e:
                print(e)
        else:
            print("nstall: Invalid action. Use 'add' or 'remove'.")

#        if rebuild:
#            rebuildOutput = ["nixos-rebuild", "switch",
#                            "-I", "nixos-config=", file_path]
#           rebuildOutput = subprocess.check_output(
#               args=rebuildOutput, shell=False)
#            print(rebuildOutput)
