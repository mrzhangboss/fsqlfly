import mockjs from 'mockjs';

export default {
  'GET /api/terminal': mockjs.mock({
    'data|5-9': [
      {
        'id|+1': 1,
        'name|+1': 1,
      },
    ],
  }),
  'GET /api/terminal/:id': (
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
            },
          ],
        }),
      },
    });
  },
  'POST  /api/transform/:id': (
    req: { params: { id: string }; body: { createAt: string } },
    res: {
      send: (arg0: {
        data: {
          id: number;
        };
      }) => void;
    },
  ) => {
    res.send({
      data: {
        id: parseInt(req.params.id, 10),
      },
    });
  },
  'POST  /api/transform/:id/stop': mockjs.mock({
    msg: '@paragraph(1000,1000)',
    success: false,
  }),
  'POST  /api/transform/debug/:id': mockjs.mock({
    msg: '@paragraph(1000,1000)',
    success: true,
  }),
};
