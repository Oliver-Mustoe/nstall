#!/usr/bin/env python3
"""

This module provides functionality for managing package installations in NixOS.

Author: Matt & Oliver

Usage:
    sudo nstall <add/remove> <package_name>

Functions:
    edit_package_list(package_name, action)

"""

# Probably need to clean these up
import sys
import subprocess
import os
import re
import json
import sqlite3
from contextlib import closing
import time

# non-stdlib imports
import toml

# TODO: Replace later with actual way to select a directory and a file (or at least a directory!)
DIR_PATH = "/etc/nixos"
FILE_PATH = f"{DIR_PATH}/configuration.nix"
DEFAULT_TOML = {"packages": {"nixpkgs": {"pks": []}}}
CONFIG_FILE_PATH = f"{DIR_PATH}/configuration.toml"


def print_pretty(input_string, color="red", newl=True):
    """
    Print the input string with specified color.

    Args:
        input_string (str): The string to be printed.
        color (str): The color to be used. Either "red" or "green".

    Returns:
        None
    """

    end = "\n" if newl else ""

    if color == "red":
        print("\033[91m" + input_string + "\033[0m", end=end)
    elif color == "green":
        print("\033[92m" + input_string + "\033[0m", end=end)
    elif color == "orange":
        print("\033[93m" + input_string + "\033[0m", end=end)
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
                print_pretty(
                    f"LOG: {package_name} is in your package list!", "orange")
            elif package_name not in config["packages"]["nixpkgs"]["pks"]:
                print_pretty(
                    f"LOG: {package_name} is not in your package list!", "orange"
                )
            else:
                print_pretty(
                    "ERROR: COULD NOT INSTALL PACKAGE FOR UNDEFINED REASON!!!", "red"
                )
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as file:
            toml.dump(config, file)
    except (IOError, toml.TomlDecodeError) as package_op_error:
        print_pretty(f"ERROR: {package_op_error}", "red")

    return do_rebuild


def search_package_list(package_name, system_hash, to_glob):
    # Create a package list SQL search based on whether or not they want globbing
    # DO NOT FORGET THE ',' AT THE END DEAR GOD DO NOT FORGET IT!!!
    if to_glob:
        package_search_query = (
            "SELECT * from packages WHERE package GLOB CONCAT (LOWER(?))"
        )
        count_package_search_query = (
            "SELECT COUNT(*) from packages WHERE package GLOB CONCAT (LOWER(?))"
        )
    else:
        package_search_query = (
            "SELECT * from packages WHERE package LIKE CONCAT (?,'%')"
        )
        count_package_search_query = (
            "SELECT COUNT(*) from packages WHERE package LIKE CONCAT (?,'%')"
        )
    # TODO: Be able to change channels
    # POSSIBLE TODO: Have building cache be its own function? Not really search when you would want to do it besides a search
    package_list_cache = f"{DIR_PATH}/{system_hash}.db"

    # Test to see if the DB exists, may eventually do 1 db, table in db is a channel
    if not os.path.isfile(package_list_cache):
        to_build_cache = True
    else:
        to_build_cache = False
    # Create db and a cursor connection
    with closing(sqlite3.connect(package_list_cache)) as connection:
        with closing(connection.cursor()) as cursor:
            if to_build_cache:
                # Create packages table
                cursor.execute(
                    "CREATE TABLE packages (package TEXT, description TEXT, version TEXT, unfree TEXT)"
                )

                # Build a JSON cache of all of the pkgs in your nixpkgs cache
                git_archive = (
                    f"https://github.com/NixOS/nixpkgs/archive/{system_hash}.tar.gz"
                )
                build_cache = [
                    "nix-env",
                    "-f",
                    git_archive,
                    "-qaP",
                    "--json",
                    "--meta",
                    "--quiet",
                    "*",
                ]
                build_output = subprocess.check_output(
                    args=build_cache, shell=False
                ).decode("utf-8")

                json_cache = json.loads(build_output)

                # Load values into the db
                for key, value in json_cache.items():
                    print(f"Creating entry for: {key}", flush=True)
                    # print(value['meta'].keys())
                    package = key

                    # For some godforsaken (misspell) reason I am getting on some that description or unfree dont exist when I can see them but whatever

                    if "description" in value["meta"]:
                        description = value["meta"]["description"]
                    else:
                        description = "n/a"

                    if value["version"] != "" and "version" in value:
                        version = value["version"]
                    else:
                        version = "n/a"

                    if "unfree" in value["meta"]:
                        unfree = value["meta"]["unfree"]
                    else:
                        unfree = "n/a"
                    cursor.execute(
                        "INSERT into packages VALUES (?,?,?,?)",
                        (package, description, version, unfree),
                    )

                print("All entries created, committing to DB...")
                connection.commit()
                print("")

            time_start = time.time()
            # Search for the users package that they want, also get the count
            matching_rows = cursor.execute(
                package_search_query, (package_name,)
            ).fetchall()
            result_amount = cursor.execute(
                count_package_search_query, (package_name,)
            ).fetchall()

            # Display the results of the searches to the user
            print("\n'Package Name' is the name you would use to install the package!")
            print_pretty(f"Results for '{target_package_name}'", "green")
            print("------------------------------------")
            for row in matching_rows:
                # DONT DO DATA CORRECTION HERE - MAKE IT GOOD IN THE DB
                package = row[0]
                description = row[1]
                version = row[2]
                unfree = row[3]
                print(
                    f"Package Name: {package}\nDescription: {description}\nVersion: {version}\n",
                    end="",
                )

                if unfree == "1":
                    print(
                        "WARNING: This package requires unfree to be enabled for the downloading channel!"
                    )
                    print("------------------------------------")
                else:
                    print("------------------------------------")
            time_end = time.time()
            print(
                f"{result_amount[0][0]} packages displayed in {time_end-time_start}!")


if __name__ == "__main__":

    if os.getuid() != 0:
        print_pretty("Usage ERROR: This script must be run as root.", "red")
        sys.exit(1)

    if len(sys.argv) < 3:
        print_pretty(
            "Usage: sudo nstall <add/remove/search/match> <package_name>", "red"
        )
        sys.exit(1)
    else:
        user_action = sys.argv[1].lower()
        target_package_name = sys.argv[2]
        rebuild = False

        if user_action in ["install", "add"]:
            rebuild = edit_package_list(
                package_name=target_package_name, action=True)
            print_pretty(
                f"SUCCESS: Added {target_package_name} to your package list!", "green"
            )
        elif user_action == "remove":
            rebuild = edit_package_list(
                package_name=target_package_name, action=False)
            print_pretty(
                f"Removed {target_package_name} from your package list!", "green"
            )
        elif user_action == "search" or user_action == "match":
            # Getting hash here for future usage of functions for other projects
            system_version = subprocess.check_output(
                args=["nixos-version"], shell=False
            ).decode("utf-8")
            system_hash = re.search(r".*\.(.*)\s\(", system_version).group(1)

            if user_action == "search":
                search_package_list(
                    package_name=target_package_name,
                    system_hash=system_hash,
                    to_glob=False,
                )
            elif user_action == "match":
                search_package_list(
                    package_name=target_package_name,
                    system_hash=system_hash,
                    to_glob=True,
                )
        else:
            print_pretty(
                "ERROR: Invalid action. Use 'add' or 'remove'.", "red")

        if rebuild:
            print_pretty(
                "LOG: Your system will need to be rebuilt to apply this configuration.",
                "orange",
            )
            print_pretty("LOG: Would you like to rebuild now? [y/n]: ", "orange", False)
            user_input = input().lower()

            if user_input == "y":
                try:
                    # Sudo may need to be placed below but I would think that program is already sudo > dont need sudo here
                    rebuild_output = ["nixos-rebuild", "switch"]
                    rebuild_output = subprocess.check_output(
                        args=rebuild_output, shell=False
                    )
                    # print(rebuild_output)
                    print_pretty("SUCCESS: Rebuild successful!", "green")
                except subprocess.CalledProcessError as rebuild_error:
                    print_pretty(f"ERROR: {rebuild_error}", "red")
            else:
                print_pretty("LOG: Rebuild skipped.", "orange")
                print_pretty(
                    "LOG: You can manually apply your configuration with the command 'sudo nixos-rebuild switch'.",
                    "orange",
                )
