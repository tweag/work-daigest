{
  pkgs ? import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/release-23.11.tar.gz";
    sha256 = "0x4s7g24mwkhf205d0dwmgcqr2jglkffn8xicwmab3crkfdr4cqh";
  }) { }
}:
pkgs.mkShell {
  name = "confluence-qa-env";
  buildInputs = with pkgs; [
    awscli2
    ssm-session-manager-plugin
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
