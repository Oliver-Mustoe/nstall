let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/archive/dbebdd67a6006bb145d98c8debf9140ac7e651d0.tar.gz";
  pkgs = import nixpkgs { };
in
pkgs.mkShellNoCC { packages = with pkgs; [ (python3.withPackages (ps: with ps; [ toml ])) black ]; }
