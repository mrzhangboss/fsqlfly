import unittest
from fsqlfly.db_helper import *
from fsqlfly.tests.base_test import FSQLFlyTestCase


class MyTestCase(FSQLFlyTestCase):
    def test_topic_reload(self):
        kafak_connector = """
properties:
- key: bootstrap.servers
  value: localhost:9092
- key: group.id
  value: {{ resource_name.database }}__{{ resource_name.name }}_group
property-version: 1
startup-mode: {{ startup_mode | default('latest-offset') }}
topic: {{ resource_name.database }}__{{ resource_name.name }}__{{ version.name }}
version: universal
        """
        real_topic = 'abcdefg'
        config = f'''
[kafka]
topic: {real_topic}
        '''
        connection = Connection(name='a', url='#', type='kafka', connector=kafak_connector)
        r_name = ResourceName(name='b', full_name='a.b', database='dd', connection=connection,
                              config=config)
        r2_name = ResourceName(name='b2', full_name='a.b2', database='dd', connection=connection)
        t_name = ResourceTemplate(name='c', resource_name=r_name, type='both', full_name='a.b.c', connection=connection)
        t2_name = ResourceTemplate(name='c2', resource_name=r2_name, type='both', full_name='a.b.c2',
                                   connection=connection)
        v_name = ResourceVersion(name='d', template=t_name, full_name='a.b.c.d', connection=connection,
                                 resource_name=r_name)
        v2_name = ResourceVersion(name='d', template=t2_name, full_name='a.b.c.d2', connection=connection,
                                  resource_name=r2_name)
        session = DBSession.get_session()

        session.add_all([connection, r_name, r2_name, t_name, t2_name, v_name, v2_name])
        session.commit()
        # cache = session.query(ResourceVersion).filter(ResourceVersion.id==v_name.id).one().generate_version_cache()
        cache = v_name.generate_version_cache()
        # cache2 = session.query(ResourceVersion).filter(ResourceVersion.id==v2_name.id).one().generate_version_cache()
        cache2 = v2_name.generate_version_cache()
        self.assertEqual(cache2['connector']['topic'], 'dd__b2__d')
        self.assertEqual(cache['connector']['topic'], real_topic)


if __name__ == '__main__':
    unittest.main()
