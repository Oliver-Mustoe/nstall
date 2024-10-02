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
DEFAULT_TOML = {"packages": {"nixpkgs": {"pks": []}}}
CONFIG_FILE_PATH = f"{DIR_PATH}/configuration.toml"

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
    do_rebuild = False

    # Check if TOML exists, if not - create it
    if not os.path.isfile(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            toml.dump(DEFAULT_TOML, f)
    try:
        # Read the toml
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as file:
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
                print_pretty(f"LOG: {package_name} is in your package list!", 'orange')
            elif package_name not in config["packages"]["nixpkgs"]["pks"]:
                print_pretty(f"LOG: {{package_name} is not in your package list!", 'orange')
            else:
                print_pretty("ERROR: COULD NOT INSTALL PACKAGE FOR UNDEFINED REASON!!!", 'red')
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as file:
            toml.dump(config, file)
    except (IOError, toml.TomlDecodeError) as package_op_error:
        print_pretty(f"ERROR: {package_op_error}", 'red')

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
            print_pretty(f"SUCCESS: Added {target_package_name} to your package list!", 'green')
        elif user_action == "remove":
            rebuild = edit_package_list(package_name=target_package_name, action=False)
            print_pretty(f"Removed {target_package_name} from your package list!", 'green')
        else:
            print_pretty("ERROR: Invalid action. Use 'add' or 'remove'.", 'red')

        if rebuild:

            print_pretty("LOG: Your system will need to be rebuilt to apply this configuration.", 'orange')
            print_pretty("LOG: Would you like to rebuild now? [y/n]", 'orange')
            user_input = input().lower()

            if user_input == "y":
                try:
                    # Sudo may need to be placed below but I would think that program is already sudo > dont need sudo here
                    rebuild_output = ["nixos-rebuild", "switch"]
                    rebuild_output = subprocess.check_output(
                        args=rebuild_output, shell=False
                    )
                    #print(rebuild_output)
                    print_pretty("SUCCESS: Rebuild successful!", 'green')
                except subprocess.CalledProcessError as rebuild_error:
                    print_pretty(f"ERROR: {rebuild_error}", 'red')
            else:
                print_pretty("LOG: Rebuild skipped.", 'orange')
                print_pretty("LOG: You can manually apply your configuration with the command 'sudo nixos-rebuild switch'.", 'orange')
