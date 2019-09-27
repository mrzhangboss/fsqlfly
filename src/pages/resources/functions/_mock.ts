import mockjs from 'mockjs';

export default {
  'GET /api/functions': mockjs.mock({
    'data|5': [
      {
        name: '@word',
        'resourceId|1-10': 1,
        className: '@word',
        constructorConfig: '@word',
        functionFrom: 'class',
        'isAvailable|1': true,
        'isPublish|1': true,
        createAt: '@datetime',
        updateAt: '@datetime',
      },
    ],
    'names|5-10': ['@word'],
    'success|1': false,
    'total|50-100': 1,
    msg: '@paragraph(1,1)',
  }),
};
