import mockjs from 'mockjs';

export default {
  'GET /api/file': mockjs.mock({
    'data|50': [
      {
        'id|+1': 1,
        name: '@word',
        info: '@paragraph(1,1)',
        'isAvailable|1': true,
        'isPublish|1': true,
        createAt: '@datetime',
        updateAt: '@datetime',
      },
    ],
    'success|1': true,
    'total|50-100': 1,
    msg: '@paragraph(1,1)',
  }),
};
