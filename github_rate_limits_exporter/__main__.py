"""
    github_rate_limits_exporter.__main__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Main entry point for ``python -m github_rate_limits_exporter``.
"""

import sys

from github_rate_limits_exporter import main

sys.exit(main(sys.argv[1:]))
