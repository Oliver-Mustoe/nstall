{
  pkgs,
  lib,
  config,
  ...
}:
let
  cfg = config.services.nstall;
  getPackages =
    toml3:
    pkgs.lib.flatten (
      map (
        channel:
        map (
          p: (import (builtins.findFile builtins.nixPath "${channel}") { config.allowUnfree = true; })."${p}"
        ) toml3.packages.${channel}.pks
      ) toml3.packages
    );
in
{
  options.services.nstall = {
    enable = lib.mkEnableOption "nstall";
    path = lib.mkOption {
      type = lib.types.str;
      default = "/etc/nixos/configuration.toml";
    };
  };

  config = lib.mkIf cfg.enable rec {
    toml2 = pkgs.lib.importTOML cfg.path;
    environment.systemPackages = getPackages (builtins.attrNames toml2);
  };
}
