# Nix expression for starting jupyter notebook
let
  pkgs   = import <nixpkgs> {inherit config; overlays=[];};
  config = {};
  # Python packages
  python = let
    packageOverrides = self: super: {
      # Disable tests in some packages
      #
      cython = super.cython.overridePythonAttrs(old: rec {
        checkPhase = "";
      });
      #
      hypothesis = super.hypothesis.overridePythonAttrs(old: rec {
        checkPhase = "";
      });
      #
      sure = super.sure.overridePythonAttrs(old: rec {
        checkPhase = "";
      });
      #
      patsy = super.patsy.overridePythonAttrs(old: rec {
        checkPhase = "";
      });
    };
    in pkgs.python37.override {inherit packageOverrides;};
  pyp = python.withPackages (ps: with ps;
    [ jupyter_core
      jupyter_client
      notebook
      ipywidgets
      #
      matplotlib
      numpy
      scipy
      pandas
      #
      
    ]);
in
  pkgs.mkShell {
    buildInputs = [ pyp ];
    shellHook   = ''
      export PYTHONPATH=$PWD
      export XDG_DATA_HOME=$PWD/.XDG
      export JUPYTER_CONFIG_DIR=$PWD/.XDG/jupyter
      '';
  }
