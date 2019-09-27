import mockjs from 'mockjs';

let ID = 1000;

function nowTime() {
  return new Date(new Date().getTime() - new Date().getTimezoneOffset() * 60000)
    .toISOString()
    .replace('T', ' ')
    .substring(0, 19);
}

export default {
  //create
  'POST /api/:model': (req: any, res: { send: (arg: { id: number }) => void }) => {
    res.send(
      mockjs.mock({
        data: { id: ID++ },
        success: true,
        msg: '@paragraph(1,1)',
        'code|1-1000': 2,
      }),
    );
  },

  // update
  'POST /api/:model/:id': (
    req: { body: { updateAt?: string } },
    res: { send: (arg: any) => void },
  ) => {
    const old = req.body;
    if (old.updateAt !== undefined) {
      old.updateAt = nowTime();
    }
    res.send(
      mockjs.mock({
        data: old,
        success: true,
        msg: '@paragraph(1,1)',
        'code|1-1000': 2,
      }),
    );
  },

  // delete
  'DELETE /api/:model/:id': mockjs.mock({
    data: null,
    success: true,
    msg: '@paragraph(1,1)',
    'code|1-1000': 2,
  }),
};
