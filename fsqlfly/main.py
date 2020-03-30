# -*- coding:utf-8 -*-
import sys
import argparse

from fsqlfly.models import delete_all_tables, create_all_tables
from fsqlfly.app import run_web


def run_webserver(commands: list):
    run_web()


def init_db(commands: list):
    create_all_tables()


def reset_db(commands: list):
    conformed_parser = argparse.ArgumentParser("Conformed")
    conformed_parser.add_argument('-f', '--force', type=bool, default=False, help='force running')
    args = conformed_parser.parse_args(commands)
    delete_all_tables(force=args.force)


def main():
    support_command = {
        "webserver": run_webserver,
        "initdb": init_db,
        "reset_db": reset_db,
    }
    args = sys.argv[1:]
    if len(args) < 1 or args[0] in ('-h', 'help') or args[0] not in support_command:
        print("Usage : fsqlfly [-h] webserver|initdb|resetdb|help")
        return
    process = support_command[args[0]]
    process(sys.argv[2:])


if __name__ == '__main__':
    main()
