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
import toml

# TODO: Replace later with actual way to select a directory and a file (or at least a directory!)
DIR_PATH = "/etc/nixos"
FILE_PATH = f"{DIR_PATH}/configuration.nix"


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
                print(f"{package_name} is in your package list!")
            elif package_name not in config["packages"]["nixpkgs"]["pks"]:
                print(f"{package_name} is not in your package list!")
            else:
                print("COULD NOT INSTALL PACKAGE FOR UNDEFINED REASON!!!")
        with open(f"{DIR_PATH}/configuration.toml", "w", encoding="utf-8") as file:
            toml.dump(config, file)
    except (IOError, toml.TomlDecodeError) as package_op_error:
        print(f"Error: {package_op_error}")

    return do_rebuild


if __name__ == "__main__":
    # Maybe add channel support
    if len(sys.argv) < 3:
        print("Usage: sudo nstall <add/remove> <package_name>")
    else:
        user_action = sys.argv[1].lower()
        target_package_name = sys.argv[2]
        rebuild = False

        if user_action in ["install", "add"]:
            rebuild = edit_package_list(package_name=target_package_name, action=True)
            # Run a nixos-rebuild
        elif user_action == "remove":
            rebuild = edit_package_list(package_name=target_package_name, action=False)
        else:
            print("nstall: Invalid action. Use 'add' or 'remove'.")

        if rebuild:
            try:
                rebuild_output = ["sudo", "nixos-rebuild", "switch"]
                rebuild_output = subprocess.check_output(
                    args=rebuild_output, shell=False
                )
                print(rebuild_output)
            except subprocess.CalledProcessError as rebuild_error:
                print(f"Rebuild Error: {rebuild_error}")
