import mockjs from 'mockjs';

export default {
  'GET /api/connection': mockjs.mock({
    'data|15': [
      {
        'id|+1': 1,
        name: '@word',
        'type|1': ['hive', 'db', 'kafka', 'hbase', 'elasticsearch', 'canal', 'file'],
        url: '@word',
        username: '@word',
        info: '@paragraph(1000,2000)',
        updateInterval: 0,
        createAt: '@datetime',
        updateAt: '@datetime',
      },
    ],
    'names|5-10': ['@word'],
    success: true,
    'total|50-100': 1,
    msg: '@paragraph(1,1)',
  }),
};
