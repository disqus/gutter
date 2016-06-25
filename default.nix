{ pkgs ? (import <nixpkgs> {}), pythonPackages ? "python35Packages" }:
let
  basePythonPackages = with builtins; if isAttrs pythonPackages
    then pythonPackages
    else getAttr pythonPackages pkgs;

  inherit (pkgs.lib) fix extends;
  elem = builtins.elem;
  basename = path: with pkgs.lib; last (splitString "/" path);
  startsWith = prefix: full: let
    actualPrefix = builtins.substring 0 (builtins.stringLength prefix) full;
  in actualPrefix == prefix;

  src-filter = path: type: with pkgs.lib;
    let
      ext = last (splitString "." path);
    in
      !elem (basename path) [".git" "__pycache__" ".eggs"] &&
      !elem ext ["egg-info" "pyc"] &&
      !startsWith "result" path;

  gutter-src = builtins.filterSource src-filter ./.;

  localOverrides = self: super: {
    gutter = super.gutter.override (attrs: {
      src = gutter-src;
    });
    durabledict = super.durabledict.override (attrs: {
      # Needs correct import from durabledict.redis, >0.9.2
      src = pkgs.fetchurl {
        url = https://github.com/disqus/durabledict/archive/17dfccdcee18da4df7c9dbc0557dc27a4ea6f3cc.zip;
        sha256 = "16xmsa57lwzd53s80id73722c0bj6378lbbfpzd6kks0rirkfpcv";
      };
    });
    traceback2 = super.traceback2.override (attrs: {
      buildInputs = attrs.buildInputs ++ (
        with super; [pbr]);
    });

    linecache2 = super.linecache2.override (attrs: {
      buildInputs = attrs.buildInputs ++ (
        with super; [pbr]);
    });
  };

  pythonPackagesWithLocals = self: basePythonPackages.override (a: {
    inherit self;
  })
  // (scopedImport {
    self = self;
    super = basePythonPackages;
    inherit pkgs;
    inherit (pkgs) fetchurl fetchgit;
  } ./python-packages.nix);

  myPythonPackages =
    (fix
    (extends localOverrides
             pythonPackagesWithLocals));

in myPythonPackages.gutter
