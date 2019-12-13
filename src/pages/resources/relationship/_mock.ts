import mockjs from 'mockjs';

export default {
  'GET /api/relationship': mockjs.mock({
    'data|7': [
      {
        'id|+1': 1,
        name: '@word',
        info: '@word',
        config: '@word',
        username: '@word',
        createAt: '@datetime',
        updateAt: '@datetime',
      },
    ],
    'names|5-10': ['@word'],
    'success|1': true,
    'total|50-100': 1,
    msg: '@paragraph(1,1)',
  })
};
