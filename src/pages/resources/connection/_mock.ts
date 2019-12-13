import mockjs from 'mockjs';

export default {
  'GET /api/connection': mockjs.mock({
    'data|15': [
      {
        'id|+1': 1,
        name: '@word',
        connectUrl: '@word',
        'connectionType|+1': ['mysql', 'hiveServer2Thrift', 'kafka'],
        connectionUrl: '@word',
        username: '@word',
        extra: '@word',
        password: 'class',

        createAt: '@datetime',
        updateAt: '@datetime',
      },
    ],
    'names|5-10': ['@word'],
    'success|1': true,
    'total|50-100': 1,
    msg: '@paragraph(1,1)',
  }),
};
