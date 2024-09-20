# nstall
Enables adding packages to a NixSphere system as you would on a more typical distribution

## Install-test
* Clone this repo
* Copy nstall.nix to /etc/nixos/ (or wherever you configuration.nix lives)
* In you configuration.nix file import nstall.nix (likely will look something like this once your done)
```bash
  imports = [
    # include NixOS-WSL modules
    ./hardware-configuration.nix
    ./nstall.nix
  ];
```
* `cd`, and then `nix-build nstall.nix`
* Add the resulting path from above command to your `environment.systemPackages` (line should have `/nix/store` in it, and end with `nstall` and the package version)
* Rebuild
* Profit ?
