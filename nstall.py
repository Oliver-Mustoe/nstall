#!/usr/bin/env python3

import sys
import subprocess
import os
import toml

# Replace later with actual way to select a directory and a file (or at least a directory!)
dir_path = "/etc/nixos"
file_path = f"{dir_path}/configuration.nix"


def edit_package_list(package_name, action):
    # TODO: add some error handling here for if a package is not in the list OR doesnt exist in general
    defaultToml = {"packages": {"nixpkgs": {"pks": []}}}
    tomlFile = f"{dir_path}/configuration.toml"
    toRebuild = False

    # Check if TOML exists, if not - create it
    if not os.path.isfile(tomlFile):
        with open(tomlFile, "w") as f:
            toml.dump(defaultToml, f)
    try:
        # Read the toml
        with open(f"{dir_path}/configuration.toml", "r") as file:
            config = toml.load(file)
            # Either add or remove the package name from the list depending on the action
            # Could probably be done with a switch statement or somethign
            if action is True and package_name not in config['packages']['nixpkgs']['pks']:
                config['packages']['nixpkgs']['pks'].append(package_name)
                toRebuild = True
            elif action is False and package_name in config['packages']['nixpkgs']['pks']:
                config['packages']['nixpkgs']['pks'].remove(package_name)
                toRebuild = True
            elif package_name in config['packages']['nixpkgs']['pks']:
                print(f"{package_name} is in your package list!")
            elif package_name not in config['packages']['nixpkgs']['pks']:
                print(f"{package_name} is not in your package list!")
            else:
                print("COULD NOT INSTALL PACKAGE FOR UNDEFINED REASON!!!")
        with open(f"{dir_path}/configuration.toml", "w") as file:
            toml.dump(config, file)
    except Exception as e:
        print(f"Error: {e}")

    return toRebuild


if __name__ == "__main__":
    # Maybe add channel support
    if len(sys.argv) < 3:
        print("Usage: sudo nstall <add/remove> <package_name>")
    else:
        action = sys.argv[1].lower()
        package_name = sys.argv[2]
        rebuild = False

        if action == "install" or action == "add":
            try:
                rebuild = edit_package_list(
                    package_name=package_name, action=True)
            except Exception as e:
                print(e)
            # Run a nixos-rebuild
        elif action == "remove":
            try:
                rebuild = edit_package_list(
                    package_name=package_name, action=False)
            except Exception as e:
                print(e)
        else:
            print("nstall: Invalid action. Use 'add' or 'remove'.")

        if rebuild:
            rebuildOutput = ["sudo", "nixos-rebuild", "switch"]
            rebuildOutput = subprocess.check_output(
                args=rebuildOutput, shell=False)
            print(rebuildOutput)
