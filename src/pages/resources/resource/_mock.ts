import mockjs from 'mockjs';

export default {
  'GET /api/resource': mockjs.mock({
    'data|50': [
      {
        'id|+1': 1,
        name: '@word',
        info: '@paragraph(1,1)',
        'namespaceId|1-8': 5,
        yaml: '@paragraph(1,1)',
        typ: 'source-table',
        'isAvailable|1': true,
        'isPublish|1': true,
        createAt: '@datetime',
        updateAt: '@datetime',
      },
    ],
    success: true,
    'total|50-100': 1,
    msg: '@paragraph(1,1)',
  }),
};
