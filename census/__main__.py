import sys

from census.validate import main

USAGE = "usage: python -m census validate [path/to/incidents.csv]"

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] != "validate":
        print(USAGE, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(args[1:]))
