"""Allow running logslice as a module: python -m logslice."""
import sys
from logslice.cli import run

sys.exit(run())
