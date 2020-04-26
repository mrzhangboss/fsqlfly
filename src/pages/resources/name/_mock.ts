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
        'isActive|1': [false, true],
        'isLocked|1': [false, true],
        createAt: '@datetime',
        updateAt: '@datetime',
        'connector|1': [
          `type: filesystem
path: "file:///path/to/whatever"`,
          '',
        ],
      },
    ],
    'names|5-10': ['@word'],
    success: true,
    'total|50-100': 1,
    msg: '@paragraph(1,1)',
  }),
  'POST /api/connection/update/:id': mockjs.mock({
    data: null,
    msg: '@cparagraph(1, 20)\n@cparagraph(1, 20)',
    'success|1': [false, true],
    'code|1': [200, 400, 500],
  }),
  'POST /api/connection/:id': mockjs.mock({
    data: null,
    msg: '@cparagraph(1, 20)\n@cparagraph(1, 20)',
    'success|1': [false, true],
    'code|1': [200, 400, 500],
  }),
  'POST /api/connection': mockjs.mock({
    data: null,
    msg: '@cparagraph(1, 20)\n@cparagraph(1, 20)',
    'success|1': [true],
    'code|1': [200, 400, 500],
  }),
};
