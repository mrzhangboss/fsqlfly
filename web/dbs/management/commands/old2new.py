# -*- coding: utf-8 -*-
import json
from django.core.management.base import BaseCommand
from dbs.models import Transform


class Command(BaseCommand):
    help = 'Convert Old DB To New'
    modes = ['require']

    def add_arguments(self, parser):

        parser.add_argument('--debug', action='store_true', help='debug')
        parser.add_argument('--mode', type=str, action='store', choices=self.modes, default='require')

    def convert_require(self, debug=True):
        for obj in Transform.objects.all():
            old = obj.require
            try:
                data = json.loads(old)
            except json.JSONDecodeError as err:
                if debug:
                    print('meet json parse error in ', obj.name)
            else:
                if isinstance(data, list):
                    names = []
                    for x in data:
                        if 'namespace' in x and 'name' in x:
                            namespace, name = x['namespace'], x['name']
                            if namespace:
                                names.append('.'.join([namespace, name]))
                            else:
                                names.append(name)
                    if debug:
                        print('New Name:', ','.join(names))

                    if names:
                        obj.require = ','.join(names)
                    else:
                        obj.require = ''

                    obj.save()

    def handle(self, *args, **options):
        mode = options['mode']
        if mode == self.modes[0]:
            self.convert_require(options['debug'])
