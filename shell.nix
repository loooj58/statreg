# Nix expression for starting jupyter notebook
let
  pkgs   = import (builtins.fetchGit {
    name = "19.03";
    url  = https://github.com/nixos/nixpkgs/;
    ref  = "release-19.03";
    rev  = "7e889fe8c81c45faf8c7964cd89eafb1f2cd6ec4";
  }) {
    config = {};
    overlays=[overlay];
  };
  #
  overlay = self: super: {
    python37 = super.python37.override { packageOverrides = pyOverrides; };
  };
  # Python overrides
  pyOverrides = self: super: {
    joblib = super.joblib.overridePythonAttrs(old: rec {
      version = "0.12.5";
      src = super.fetchPypi {
        inherit version;
        pname  = "joblib";
        sha256 = "11cdfd38cdb71768149e1373f2509e9b4fc1ec6bc92f874cb515b25f2d69f8f4";
      };
    });
  };
  #
  pyp = pkgs.python37.withPackages (ps: with ps; [
    jupyter_core
    jupyter_client
    notebook
    #
    matplotlib
    seaborn
    numpy
    sympy
    scipy
    pandas
    #
    pymc3
  ]);
in
#pkgs.mkShell {buildInputs = [pkgs.clblas]; }
pkgs.mkShell {
  buildInputs = [ pyp ];
  # TMP&Co overrides needed for Theano https://github.com/NixOS/nixpkgs/issues/4546
  shellHook   = ''
    export PYTHONPATH=$PWD:$PWD/unfolding
    export XDG_DATA_HOME=$PWD/.XDG
    export JUPYTER_CONFIG_DIR=$PWD/.XDG/jupyter
    export TMP=/tmp
    export TMPDIR=/tmp
    export TEMPDIR=/tmp
    export TEMP=/tmp
    '';
}
