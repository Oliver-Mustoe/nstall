{
  description = "nstall flake for build + module";

  inputs = {
    nixpkgs.url = "https://github.com/NixOS/nixpkgs/archive/dbebdd67a6006bb145d98c8debf9140ac7e651d0.tar.gz";
  };

  # Eventually probable want something like flake-utils here to support building for my non-NixOS homies
  outputs = { self, nixpkgs, ...}: 
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in
    rec {
      # Build nstall
      packages.x86_64-linux.default = import ./nstall_build.nix { inherit pkgs; };

      # Add the module
      nixosModules.default = import ./nstall-flake.nix;

      nstall-overlay = final: prev: {
        nstall = packages.x86_64-linux.default;
      };
    };
}
