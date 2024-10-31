{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "https://github.com/NixOS/nixpkgs/archive/dbebdd67a6006bb145d98c8debf9140ac7e651d0.tar.gz";
  };

  # Eventually probable want something like flake-utils here to support building for my non-NixOS homies
  outputs = { self, nixpkgs, ...}: 
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in
    {
      packages.x86_64-linux.default = import ./nstall_build.nix { inherit pkgs; };
    };
}
