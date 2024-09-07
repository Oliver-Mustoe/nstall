# nstall
Enables adding packages to a NixSphere system as you would on a more typical distribution

## Install-test
* Clone this repo
* `cd`, and then `nix-build nstall.nix`
* Add the resulting path from above command to your `environment.systemPackages` (line should have `/nix/store` in it, and end with `nstall` and the package version)
* Rebuild
* Profit ?