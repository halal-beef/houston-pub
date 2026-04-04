{
  description = "houston";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    {
      self,
      nixpkgs,
      ...
    }:
    let
      forAllSystems = nixpkgs.lib.genAttrs [
        "x86_64-linux"
        "aarch64-linux"
      ];
    in
    {
      formatter = forAllSystems (system: nixpkgs.legacyPackages.${system}.nixfmt-tree);
      packages = forAllSystems (system: {
        default = self.packages.${system}.houston;
        houston = nixpkgs.legacyPackages.${system}.callPackage (
          {
            lib,
            stdenv,
            python3,
            python3Packages,
            autoPatchelfHook,
            writeShellScriptBin,
            fetchPypi,
            udev,
          }:
          let
            pkg-about-override = python3Packages.pkg-about.overrideAttrs (prev: rec {
              version = "1.3.1";
              src = fetchPypi {
                pname = "pkg_about";
                inherit version;
                hash = "sha256-EyD4GS/iU31ucsBvpBkcY9SgvBX1lYxQH8vvAcW4PCY=";
              };
            });
            libusb = python3Packages.buildPythonPackage rec {
              pname = "libusb";
              version = "1.0.28";
              pyproject = true;

              src = fetchPypi {
                inherit pname version;
                hash = "sha256-8Ylppy6caIFiV7uhPvWD8kX+s9WS+8QuxYeWAegGUWc=";
              };

              dependencies = with python3Packages; [
                pkg-about-override
                setuptools
                tox
              ];

              nativeBuildInputs = [
                autoPatchelfHook
              ];

              buildInputs = [
                udev
              ];

              buildSystem = with python3Packages; [
                setuptools
              ];
            };
          in
          stdenv.mkDerivation {
            name = "houston";
            installPhase = ''
              install -Dm555 ${lib.getExe (
                writeShellScriptBin "houston" ''
                  ${
                    lib.getExe (
                      python3.withPackages (
                        pythonPkgs: with pythonPkgs; [
                          coloredlogs
                          libusb
                          lz4
                          pygments
                          pyusb
                        ]
                      )
                    )
                  } ${./houston.py} $@
                ''
              )} $out/bin/houston
            '';
            dontUnpack = true;
            meta.mainProgram = "houston";
          }
        ) { };
      });
    };
}
