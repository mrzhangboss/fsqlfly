import mockjs from 'mockjs';

export default {
  'GET /api/connector': mockjs.mock({
    'data|15': [
      {
        'id|+1': 1,
        name: '@word',
        'type|1': ['system', 'canal'],
        info: '@paragraph(1000,2000)',
        'sourceId|1': [1, 2, 3],
        'targetId|1': [1, 2, 3],
        'isLocked|1': [false, true],
        createAt: '@datetime',
        updateAt: '@datetime',
        config: `
[db]
insert_primary_key = false

[kafka]
process_time_enable = true
process_time_name = flink_process_time
rowtime_enable = true
rowtime_from = MYSQL_DB_EXECUTE_TIME
        `,

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
  'POST /api/connector/update/:id': mockjs.mock({
    data: null,
    msg: '@cparagraph(1, 20)\n@cparagraph(1, 20)',
    'success|1': [false, true],
    'code|1': [200, 400, 500],
  }),
  'POST /api/connector/:id': mockjs.mock({
    data: null,
    msg: '@cparagraph(1, 20)\n@cparagraph(1, 20)',
    'success|1': [false, true],
    'code|1': [200, 400, 500],
  }),
  'POST /api/connector': mockjs.mock({
    data: null,
    msg: '@cparagraph(1, 20)\n@cparagraph(1, 20)',
    'success|1': [true],
    'code|1': [200, 400, 500],
  }),
};
