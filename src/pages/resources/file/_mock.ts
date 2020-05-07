import mockjs from 'mockjs';

export default {
  'GET /api/file': mockjs.mock({
    'data|50': [
      {
        'id|+1': 1,
        name: '@word',
        info: '@paragraph(1,1)',
        'isActive|1': true,
        'isLocked|1': false,
        createAt: '@datetime',
        updateAt: '@datetime',
      },
    ],
    success: true,
    'total|50-100': 1,
    msg: '@paragraph(1,1)',
  }),
};
