{
  durabledict = super.buildPythonPackage {
    name = "durabledict-0.9.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/b2/b4/055cafa805ff3872c51371825e88119ac40d3ff09597505ffe407ced33a7/durabledict-0.9.2.tar.gz";
      md5 = "e656bd013fcd41cf74566b1ccf672adc";
    };
  };
  gutter = super.buildPythonPackage {
    name = "gutter-0.6.0";
    buildInputs = with self; [nose exam mock django redis];
    doCheck = true;
    propagatedBuildInputs = with self; [durabledict jsonpickle werkzeug six];
    src = ./.;
  };
  jsonpickle = super.buildPythonPackage {
    name = "jsonpickle-0.9.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/2a/9f/bc2833f0c0dbe2bcca7684765ca93ec34344704b9d27a3a2e0f362bad8e9/jsonpickle-0.9.3.tar.gz";
      md5 = "cb30198969da11f9d19a11d03e0d0046";
    };
  };
  six = super.buildPythonPackage {
    name = "six-1.10.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/b3/b2/238e2590826bfdd113244a40d9d3eb26918bd798fc187e2360a8367068db/six-1.10.0.tar.gz";
      md5 = "34eed507548117b2ab523ab14b2f8b55";
    };
  };
  werkzeug = super.buildPythonPackage {
    name = "werkzeug-0.11.10";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/b7/7f/44d3cfe5a12ba002b253f6985a4477edfa66da53787a2a838a40f6415263/Werkzeug-0.11.10.tar.gz";
      md5 = "780967186f9157e88f2bfbfa6f07a893";
    };
  };

### Test requirements

  django = super.buildPythonPackage {
    name = "django-1.9.7";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/50/76/aeb1bdde528b23e76df5964003e3e4e734c57c74e7358c3b2224987617dd/Django-1.9.7.tar.gz";
      md5 = "7de9ba83bfe01f4b7d45645c1b259c83";
    };
  };
  exam = super.buildPythonPackage {
    name = "exam-0.10.6";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [mock];
    src = fetchurl {
      url = "https://pypi.python.org/packages/c7/bd/c15ce029540bb1b551af83c0df502ba47e019ce7132a65db046ad16b8eda/exam-0.10.6.tar.gz";
      md5 = "0bf84acc2427a8a3d58d13d7297ff84a";
    };
  };
  mock = super.buildPythonPackage {
    name = "mock-2.0.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pbr six];
    src = fetchurl {
      url = "https://pypi.python.org/packages/0c/53/014354fc93c591ccc4abff12c473ad565a2eb24dcd82490fae33dbf2539f/mock-2.0.0.tar.gz";
      md5 = "0febfafd14330c9dcaa40de2d82d40ad";
    };
  };
  nose = super.buildPythonPackage {
    name = "nose-1.3.7";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/58/a5/0dc93c3ec33f4e281849523a5a913fa1eea9a3068acfa754d44d88107a44/nose-1.3.7.tar.gz";
      md5 = "4d3ad0ff07b61373d2cefc89c5d0b20b";
    };
  };
  pbr = super.buildPythonPackage {
    name = "pbr-1.10.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/c3/2c/63275fab26a0fd8cadafca71a3623e4d0f0ee8ed7124a5bb128853d178a7/pbr-1.10.0.tar.gz";
      md5 = "8e4968c587268f030e38329feb9c8f17";
    };
  };
  redis = super.buildPythonPackage {
    name = "redis-2.10.5";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/68/44/5efe9e98ad83ef5b742ce62a15bea609ed5a0d1caf35b79257ddb324031a/redis-2.10.5.tar.gz";
      md5 = "3b26c2b9703b4b56b30a1ad508e31083";
    };
  };
}
