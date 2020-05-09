# -*- coding:utf-8 -*-
import sys
import argparse
import logzero
from os.path import join, dirname, abspath


def run_webserver(commands: list):
    extend_command = None
    if '--jobdaemon' in commands:
        from fsqlfly.job_manager.daemon import FlinkJobDaemon
        from fsqlfly import settings
        daemon = FlinkJobDaemon(settings.FSQLFLY_FINK_HOST,
                                settings.FSQLFLY_JOB_DAEMON_MAX_TRY_ONE_DAY,
                                settings.FSQLFLY_JOB_LOG_FILE)
        extend_command = daemon.get_periodic_callback(settings.FSQLFLY_JOB_DAEMON_FREQUENCY)
        logzero.logger.debug('add job daemon command {}: {}: {}: {}'.format(settings.FSQLFLY_FINK_HOST,
                                                                            settings.FSQLFLY_JOB_DAEMON_MAX_TRY_ONE_DAY,
                                                                            settings.FSQLFLY_JOB_LOG_FILE,
                                                                            settings.FSQLFLY_JOB_DAEMON_FREQUENCY))

    from fsqlfly.app import run_web
    try:
        run_web(extend_command=extend_command)
    except KeyboardInterrupt:
        logzero.logger.info("Stop Web...")


def run_canal(commands: list):
    from fsqlfly.canal_manager.canal_consumer import CanalConsumer
    CanalConsumer().execute()


def run_load_mysql_resource(commands: list):
    from fsqlfly.canal_manager.load_mysql_resource import LoadMySQLResource
    LoadMySQLResource().execute()


def init_db(commands: list):
    from fsqlfly.db_helper import DBDao

    DBDao.create_all_tables()


def reset_db(commands: list):
    from fsqlfly.db_helper import DBDao
    conformed_parser = argparse.ArgumentParser("Conformed")
    conformed_parser.add_argument('-f', '--force', type=bool, default=False, help='force running')
    args = conformed_parser.parse_args(commands)
    DBDao.delete_all_tables(force=args.force)


def run_echo_env(commands: list):
    if len(commands) > 0:
        out = open(commands[0], 'w')
    else:
        out = sys.stdout

    lib_path = dirname(abspath(__file__))
    print(open(join(lib_path, 'env.template'), 'r').read(), file=out)


def run_db2hive(comands: list):
    from fsqlfly.helper import DBToHive
    DBToHive.run(comands)


def run_canal(commands: list):
    from fsqlfly.contrib.canal import Consumer
    Consumer.build(commands[0]).run()


def main():
    support_command = {
        "echoenv": run_echo_env,
        "webserver": run_webserver,
        "initdb": init_db,
        "resetdb": reset_db,
        "runcanal": run_canal
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
