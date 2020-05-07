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
        'isLocked|1': false,
        'isActive|1': true,
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
