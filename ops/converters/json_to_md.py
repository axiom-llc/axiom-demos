#!/usr/bin/env python3

import json
import sys


def markdown(value, level=1):
    if isinstance(value, dict):
        out = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                out.append(f"{'#' * level} {key}\n")
                out.append(markdown(item, level + 1))
            else:
                out.append(f"- **{key}:** {scalar(item)}\n")
        return "\n".join(out)

    if isinstance(value, list):
        out = []
        for item in value:
            if isinstance(item, (dict, list)):
                out.append(markdown(item, level))
            else:
                out.append(f"- {scalar(item)}")
        return "\n".join(out)

    return scalar(value)


def scalar(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} FILE.json")

    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)

    print(markdown(data))


if __name__ == "__main__":
    main()
