{ pkgs ? import <nixpkgs> {} }:

with pkgs;

mkShell {
  buildInputs = with pkgs;  [
    grpc-tools
    poetry
    xorg.libX11
    gnumake
  ];
  LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${
      with pkgs;
      lib.makeLibraryPath [ libGL xorg.libX11 xorg.libXi xorg.libXcursor libxkbcommon stdenv.cc.cc]
    }";
}
