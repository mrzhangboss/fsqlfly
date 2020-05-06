import mockjs from 'mockjs';

const avatars = [
  'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png', // Alipay
  'https://gw.alipayobjects.com/zos/rmsportal/zOsKZmFRdUtvpqCImOVY.png', // Angular
  'https://gw.alipayobjects.com/zos/rmsportal/dURIMkkrRFpPgTuzkwnB.png', // Ant Design
  'https://gw.alipayobjects.com/zos/rmsportal/sfjbOqnsXXJgNCjCzDBL.png', // Ant Design Pro
  'https://gw.alipayobjects.com/zos/rmsportal/siCrBXXhmvTQGWPNLBow.png', // Bootstrap
  'https://gw.alipayobjects.com/zos/rmsportal/kZzEzemZyKLKFsojXItE.png', // React
  'https://gw.alipayobjects.com/zos/rmsportal/ComBAopevLwENQdKWiIn.png', // Vue
  'https://gw.alipayobjects.com/zos/rmsportal/nxkuOJlFJuAUhzlMTCEe.png', // Webpack
];

function nowTime() {
  return new Date(new Date().getTime() - new Date().getTimezoneOffset() * 60000)
    .toISOString()
    .replace('T', ' ')
    .substring(0, 19);
}

let gId = 60;
export default {
  'GET /api/transform/info': mockjs.mock({
    data: {
      namespaces: [
        { id: 0, name: 'default' },
        { id: 1, name: 'cat' },
        { id: 2, name: 'dog' },
        {
          id: 3,
          name: 'bird',
        },
      ],
      'columns|35': [
        {
          'id|+1': 1,
          name: '@word',
          'namespace|1': ['cat', 'dog', 'bird'],
          info: '@paragraph(1,1)',
          rowtime: '',
          proctime: '',
          'disabled|1': [true, false, false, false, false, false, false, false],
          'avatar|1': avatars,
          'columns|2-3': [{ name: '@word', 'id|+1': 1 }],
        },
      ],
      success: true,
    },
  }),
  'GET /api/transform': mockjs.mock({
    'data|5-9': [
      {
        'id|+1': 1,
        name: '@word',
        'namespaceId|+1': 1,
        info: '@paragraph(1,1)',
        'avatar|1': avatars,
        'isAvailable|1': true,
        'isPublish|1': true,
        createAt: '@datetime',
        updateAt: '@datetime',
        require: 'sdfsdf.sdf,sdfe.sd',
        sql: 'select * from shit',
        config: '-name: jack\n-type:time',
      },
    ],
    success: true,
  }),
  'GET /api/require': mockjs.mock({
    'data|5-9': ['@word'],
    success: true,
  }),

  'GET /api/transform/:id': (
    req: { params: { id: string }; body: { createAt: string } },
    res: { send: (arg0: { data: any }) => void },
  ) => {
    res.send({
      data: {
        detail: {
          sql: 'select * from shit',
          config: '-name: jack\n-type:time',
        },
        resources: mockjs.mock({
          'columns|5': [
            {
              'id|+1': 1,
              name: '@word',
              'namespace|1': ['cat', 'dog', 'bird'],
              info: '@paragraph(1,1)',
              'avatar|1': avatars,
            },
          ],
        }),
      },
    });
  },
  'POST  /api/transform': (
    req: any,
    res: {
      send: (arg0: {
        data: {
          id: number;
          createAt: string;
          updateAt: string;
          avatar: string;
        };
      }) => void;
    },
  ) => {
    res.send({
      data: {
        id: gId++,
        createAt: nowTime(),
        updateAt: nowTime(),
        avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
      },
    });
  },
  'POST  /api/transform/:id': (
    req: { params: { id: string }; body: { createAt: string } },
    res: {
      send: (arg0: {
        data: {
          id: number;
          createAt: string;
          updateAt: string;
          avatar: string;
        };
      }) => void;
    },
  ) => {
    res.send({
      data: {
        id: parseInt(req.params.id, 10),
        updateAt: nowTime(),
        createAt: req.body.createAt,
        avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
      },
    });
  },
  'POST  /api/transform/:id/run': mockjs.mock({
    msg: '@paragraph(1000,1000)',
    success: false,
  }),
  'POST  /api/transform/debug/:id': mockjs.mock({
    msg: '@paragraph(1000,1000)',
    success: true,
  }),
};
