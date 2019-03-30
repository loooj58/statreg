# Nix expression for starting jupyter notebook
let
  pkgs    = import <nixpkgs> {config = {}; overlays=[overlay];};
  overlay = self: super: {
    # Still broken
    clblas = self.lib.overrideDerivation super.clblas (oldAttrs: {
      cmakeFlags = [];
    });
    python37 = super.python37.override { packageOverrides = pyOverrides; };
  };
  # Python overrides
  pyOverrides = self: super: {
    libgpuarray = super.libgpuarray.override {
      openclSupport = false;
    };
#    Theano = self.callPackage ./nix/Theano.nix rec {
#      cudaSupport = self.config.cudaSupport or false;
#      cudnnSupport = cudaSupport;
#      inherit (pkgs.linuxPackages) nvidia_x11;
#    };
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
  shellHook   = ''
    export PYTHONPATH=$PWD:$PWD/unfolding
    export XDG_DATA_HOME=$PWD/.XDG
    export JUPYTER_CONFIG_DIR=$PWD/.XDG/jupyter
    '';
}
