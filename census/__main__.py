import sys

USAGE = "usage: python -m census validate [path/to/incidents.csv] | python -m census openfda [options] | python -m census nhtsa [options]"

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "validate":
        from census.validate import main
    elif args and args[0] == "openfda":
        from census.openfda import main
    elif args and args[0] == "nhtsa":
        from census.nhtsa import main
    else:
        print(USAGE, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(args[1:]))
