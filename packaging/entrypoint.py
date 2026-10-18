"""Entry point used only when building standalone binaries with PyInstaller.

It is a thin wrapper around ``filmweb.main:main``:

* ``main.py`` uses relative imports, so it cannot be used as a PyInstaller
  script directly - it has to be imported as part of the ``filmweb`` package.
* ``filmweb`` uses ``multiprocessing.Pool``. In a frozen Windows executable
  ``freeze_support()`` must be called first, otherwise every worker process
  would start the whole program again.
"""

import multiprocessing

from filmweb.main import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
