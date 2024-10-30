
let
  # where does the hash come from?
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/archive/dbebdd67a6006bb145d98c8debf9140ac7e651d0.tar.gz";
  pkgs = import nixpkgs { };
in
  pkgs.callPackage ./nstall_build.nix { }
