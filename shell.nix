{
  pkgs ? import (builtins.fetchTarball {
    # Branch: nixos-unstable
    url = "https://github.com/NixOS/nixpkgs/archive/92236affa23a5a44ade5fa78e31c674a10b2ab94.tar.gz";
    sha256 = "0q478xh71h4alnaangz8ayk3xffnr08wawbk84cd4rqgisj7qk6f";
  }) { }
}:
pkgs.mkShell {
  name = "confluence-qa-env";
  buildInputs = with pkgs; [
    python311
    poetry
  ];
  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib";
    poetry env use "${pkgs.python311}/bin/python"
    poetry install --sync --with=dev
    source "$(poetry env info --path)/bin/activate"
  '';
}
