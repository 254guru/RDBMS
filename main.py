#!/usr/bin/env python3
"""
Main entry point for the RDBMS REPL.
"""

import sys
from rdbms.repl import REPL


def main():
    """Start the REPL."""
    repl = REPL()
    repl.run()


if __name__ == "__main__":
    main()
