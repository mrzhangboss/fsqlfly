import mockjs from 'mockjs';

export default {
  'GET /api/template': mockjs.mock({
    'data|15': [
      {
        'id|+1': 1,
        name: '@word',
        fullName: '@paragraph(100,1000)',
        'type|1': ['sink', 'source', 'both'],
        info: '@cparagraph(1000,2000)',
        'isDefault|1': [false, true],
        'isSystem|1': [false, true],
        'isLocked|1': [false, true],
        config: '',
        createAt: '@datetime',
        updateAt: '@datetime',
      },
    ],
    success: true,
    msg: '@paragraph(1,1)',
  }),
  'POST /api/template/update/:id': mockjs.mock({
    data: null,
    msg: '@cparagraph(1, 20)\n@cparagraph(1, 20)',
    'success|1': [false, true],
    'code|1': [200, 400, 500],
  }),
  'POST /api/name/:id': mockjs.mock({
    data: null,
    msg: '@cparagraph(1, 20)\n@cparagraph(1, 20)',
    'success|1': [false, true],
    'code|1': [200, 400, 500],
  }),
  'POST /api/name': mockjs.mock({
    data: null,
    msg: '@cparagraph(1, 20)\n@cparagraph(1, 20)',
    'success|1': [true],
    'code|1': [200, 400, 500],
  }),
};
