import mockjs from 'mockjs';

let ID = 1000;

function nowTime() {
  return new Date(new Date().getTime() - new Date().getTimezoneOffset() * 60000)
    .toISOString()
    .replace('T', ' ')
    .substring(0, 19);
}

const updateMethod = (req: { body: { updateAt?: string } }, res: { send: (arg: any) => void }) => {
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
};
export default {
  //create
  'POST /notapi/:model': (req: any, res: { send: (arg: { id: number }) => void }) => {
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
  'POST /api/connection/:id': updateMethod,
  'POST /api/file/:id': updateMethod,
  'POST /api/functions/:id': updateMethod,
  'POST /api/relationship/:id': updateMethod,
  'POST /api/resource/:id': updateMethod,

  // delete
  'DELETE /api/:model/:id': mockjs.mock({
    data: null,
    success: true,
    msg: '@paragraph(1,1)',
    'code|1-1000': 2,
  }),
};
