{ pkgs }: {
  deps = [
    pkgs.postgresql
    pkgs.libxcrypt
    pkgs.file
    pkgs.python310Packages.tensorflow
    pkgs.python310Packages.dlib
    pkgs.python310Packages.typing-extensions
    pkgs.python310Packages.pydantic
    pkgs.python310Packages.fastapi
    pkgs.nano
    pkgs.libGL
    pkgs.libGLU
    pkgs.glibc
    pkgs.opencv4
    pkgs.python310Packages.keras
    pkgs.python310Packages."imap-tools"
  ];

  shellHook = ''
    export LD_LIBRARY_PATH=${pkgs.libGL.out}/lib:${pkgs.libGLU.out}/lib:${pkgs.glibc}/lib:${pkgs.opencv4.out}/lib:$LD_LIBRARY_PATH
    export PYTHONPATH=.:$PYTHONPATH
  '';
}
