import mockjs from 'mockjs';

export default {
  'GET /api/namespace': mockjs.mock({
    'data|29': [
      {
        'id|+1': 1,
        'name|1': ['@word', '@paragraph(20,30)'],
        info: '@paragraph(1,1)',
        'avatar|1': [
          'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png', // Alipay
          'https://gw.alipayobjects.com/zos/rmsportal/zOsKZmFRdUtvpqCImOVY.png', // Angular
          'https://gw.alipayobjects.com/zos/rmsportal/dURIMkkrRFpPgTuzkwnB.png', // Ant Design
          'https://gw.alipayobjects.com/zos/rmsportal/sfjbOqnsXXJgNCjCzDBL.png', // Ant Design Pro
          'https://gw.alipayobjects.com/zos/rmsportal/siCrBXXhmvTQGWPNLBow.png', // Bootstrap
          'https://gw.alipayobjects.com/zos/rmsportal/kZzEzemZyKLKFsojXItE.png', // React
          'https://gw.alipayobjects.com/zos/rmsportal/ComBAopevLwENQdKWiIn.png', // Vue
          'https://gw.alipayobjects.com/zos/rmsportal/nxkuOJlFJuAUhzlMTCEe.png', // Webpack
        ],
        'isAvailable|1': true,
        'isPublish|1': true,
        createAt: '@datetime',
        updateAt: '@datetime',
      },
    ],
    success: true,
    msg: '@paragraph(1,1)',
    'code|1-1000': 2,
  }),
};
