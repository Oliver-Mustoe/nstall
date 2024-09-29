{ pkgs, ... }:
let
  toml = pkgs.lib.importTOML ./configuration.toml;
  getPackages =
    pkgsList:
    pkgs.lib.flatten (
      map (
        channel:
        map (
          p: (import (builtins.findFile builtins.nixPath "${channel}") { config.allowUnfree = true; })."${p}"
        ) toml.packages.${channel}.pks
      ) pkgsList
    );
  packages = getPackages (builtins.attrNames toml.packages);
in
{
  environment.systemPackages = packages;
}
