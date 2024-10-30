{ pkgs ? import <nixpkgs> {} }:

pkgs.python3Packages.buildPythonApplication rec {
    pname = "nstall";
    version = "0.3";
    format = "other";

     propagatedBuildInputs = [
         # List of dependencies
         pkgs.python3Packages.toml
     ];

    # Add further lines to `installPhase` to install any extra data files if needed.
    dontUnpack = true;
    installPhase = ''
        install -Dm755 ${./nstall.py} $out/bin/${pname}
    '';
}
