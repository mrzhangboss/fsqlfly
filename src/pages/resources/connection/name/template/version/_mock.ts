import mockjs from 'mockjs';

export default {
  'GET /api/version': mockjs.mock({
    'data|15': [
      {
        'id|+1': 1,
        'name|1': ['@word', null],
        fullName: '@paragraph(100,1000)',
        'type|1': ['sink', 'source', 'both'],
        info: '@cparagraph(1000,2000)',
        'isDefault|1': [false, true],
        'isSystem|1': [false, true],
        'isLocked|1': [false, true],
        config: '',
        'version|+1': 1,
        createAt: '@datetime',
        updateAt: '@datetime',
      },
    ],
    success: true,
    msg: '@paragraph(1,1)',
  }),
  'POST /api/version/update/:id': mockjs.mock({
    data: null,
    msg: '@cparagraph(1, 20)\n@cparagraph(1, 20)',
    'success|1': [false, true],
    'code|1': [200, 400, 500],
  }),
  'POST /api/version/:id': mockjs.mock({
    data: null,
    msg: '@cparagraph(1, 20)\n@cparagraph(1, 20)',
    'success|1': [true],
    'code|1': [200, 400, 500],
  }),
  'POST /api/version': mockjs.mock({
    data: null,
    msg: '@cparagraph(1, 20)\n@cparagraph(1, 20)',
    'success|1': [true],
    'code|1': [200, 400, 500],
  }),
};
