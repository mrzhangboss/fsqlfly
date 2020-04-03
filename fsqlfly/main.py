# -*- coding:utf-8 -*-
import sys
import argparse
import logzero


def run_webserver(commands: list):
    from fsqlfly.app import run_web
    try:
        run_web()
    except KeyboardInterrupt:
        logzero.logger.info("Stop Web...")


def run_canal(commands: list):
    from fsqlfly.canal_manager.canal_consumer import CanalConsumer
    CanalConsumer().execute()


def run_load_mysql_resource(commands: list):
    from fsqlfly.canal_manager.load_mysql_resource import LoadMySQLResource
    LoadMySQLResource().execute()


def run_job_daemon(commands: list):
    from fsqlfly import settings
    from fsqlfly.job_manager.daemon import FlinkJobDaemon
    daemon = FlinkJobDaemon(settings.FSQLFLY_FINK_HOST,
                            settings.FSQLFLY_JOB_DAEMON_FREQUENCY,
                            settings.FSQLFLY_JOB_DAEMON_MAX_TRY_ONE_DAY,
                            settings.FSQLFLY_JOB_LOG_FILE)
    print('daemon running...')
    daemon.run()


def init_db(commands: list):
    from fsqlfly.models import create_all_tables

    create_all_tables()


def reset_db(commands: list):
    from fsqlfly.models import delete_all_tables
    conformed_parser = argparse.ArgumentParser("Conformed")
    conformed_parser.add_argument('-f', '--force', type=bool, default=False, help='force running')
    args = conformed_parser.parse_args(commands)
    delete_all_tables(force=args.force)


def run_echo_env(commands: list):
    if len(commands) > 0:
        out = open(commands[0], 'w')
    else:
        out = sys.stdout
    import os
    from fsqlfly import settings
    print(open(os.path.join(settings.ROOT_DIR, 'env.template'), 'r').read(), file=out)


def main():
    support_command = {
        "echoenv": run_echo_env,
        "webserver": run_webserver,
        "initdb": init_db,
        "resetdb": reset_db,
        "jobdaemon": run_job_daemon,
        "loadmysql": run_load_mysql_resource,
        "canal": run_canal,
    }
    args = sys.argv[1:]
    method = args[0] if len(args) > 0 else 'help'
    if len(args) == 0 or method in ('-h', 'help') or method not in support_command:
        print("Usage : fsqlfly [-h] {}".format('|'.join(list(support_command.keys()) + ['help'])))
        return
    process = support_command[args[0]]
    process(sys.argv[2:])


if __name__ == '__main__':
    main()
