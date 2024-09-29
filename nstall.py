#!/usr/bin/env python3
"""

This module provides functionality for managing package installations in NixOS.

Author: Matt & Oliver

Usage:
    sudo nstall <add/remove> <package_name>

Functions:
    edit_package_list(package_name, action)

"""

import sys
import subprocess
import os

# non-stdlib imports
import toml

# TODO: Replace later with actual way to select a directory and a file (or at least a directory!)
DIR_PATH = "/etc/nixos"
FILE_PATH = f"{DIR_PATH}/configuration.nix"

def print_pretty(input_string, color='red'):
    """
    Print the input string with specified color.

    Args:
        input_string (str): The string to be printed.
        color (str): The color to be used. Either "red" or "green".

    Returns:
        None
    """
    if color == "red":
        print("\033[91m" + input_string + "\033[0m")
    elif color == "green":
        print("\033[92m" + input_string + "\033[0m")
    elif color == "orange":
        print("\033[93m" + input_string + "\033[0m")
    else:
        print(input_string)

def edit_package_list(package_name, action):
    """
    Edit the package list in the configuration.toml file.

    Args:
        package_name (str): The name of the package.
        action (bool): True to add the package to the list, False to remove it.

    Returns:
        bool: True if the configuration file needs to be rebuilt, False otherwise.
    """
    # TODO: add some error handling here for if a package is not
    # in the list OR doesnt exist in general
    default_toml = {"packages": {"nixpkgs": {"pks": []}}}
    toml_file = f"{DIR_PATH}/configuration.toml"
    do_rebuild = False

    # Check if TOML exists, if not - create it
    if not os.path.isfile(toml_file):
        with open(toml_file, "w", encoding="utf-8") as f:
            toml.dump(default_toml, f)
    try:
        # Read the toml
        with open(f"{DIR_PATH}/configuration.toml", "r", encoding="utf-8") as file:
            config = toml.load(file)
            # Either add or remove the package name from the list depending on the action
            # Could probably be done with a switch statement or somethign
            if (
                action is True
                and package_name not in config["packages"]["nixpkgs"]["pks"]
            ):
                config["packages"]["nixpkgs"]["pks"].append(package_name)
                do_rebuild = True
            elif (
                action is False and package_name in config["packages"]["nixpkgs"]["pks"]
            ):
                config["packages"]["nixpkgs"]["pks"].remove(package_name)
                do_rebuild = True
            elif package_name in config["packages"]["nixpkgs"]["pks"]:
                print_pretty(f"{package_name} is in your package list!", 'red')
            elif package_name not in config["packages"]["nixpkgs"]["pks"]:
                print_pretty(f"{package_name} is not in your package list!", 'red')
            else:
                print_pretty("COULD NOT INSTALL PACKAGE FOR UNDEFINED REASON!!!", 'red')
        with open(f"{DIR_PATH}/configuration.toml", "w", encoding="utf-8") as file:
            toml.dump(config, file)
    except (IOError, toml.TomlDecodeError) as package_op_error:
        print_pretty(f"Error: {package_op_error}", 'red')

    return do_rebuild


if __name__ == "__main__":
    # Maybe add channel support
    if len(sys.argv) < 3:
        print_pretty("Usage: sudo nstall <add/remove> <package_name>", 'red')
    else:
        user_action = sys.argv[1].lower()
        target_package_name = sys.argv[2]
        rebuild = False

        if user_action in ["install", "add"]:
            rebuild = edit_package_list(package_name=target_package_name, action=True)
            print_pretty(f"Added {target_package_name} to your package list!", 'green')
        elif user_action == "remove":
            rebuild = edit_package_list(package_name=target_package_name, action=False)
            print_pretty(f"Removed {target_package_name} from your package list!", 'green')
        else:
            print_pretty("nstall: Invalid action. Use 'add' or 'remove'.", 'red')

        if rebuild:

            print_pretty("You should now rebuild your system configuration.", 'orange')
            print_pretty("Would you like to rebuild now? [y/n]", 'orange')
            user_input = input().lower()

            if user_input == "y":
                try:
                    rebuild_output = ["sudo", "nixos-rebuild", "switch"]
                    rebuild_output = subprocess.check_output(
                        args=rebuild_output, shell=False
                    )
                    #print(rebuild_output)
                    print_pretty("Rebuild successful!", 'green')
                except subprocess.CalledProcessError as rebuild_error:
                    print_pretty(f"Rebuild Error: {rebuild_error}", 'red')
            else:
                print_pretty("Rebuild skipped.", 'orange')
                print_pretty("Please remember to rebuild your system configuration.", 'orange')
                print_pretty("You can do this by running 'sudo nixos-rebuild switch'.", 'orange')