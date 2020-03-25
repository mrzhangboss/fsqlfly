import mockjs from 'mockjs';

export default {
  'GET /api/blank': (req: any, res: { send: (arg0: string) => void }) => {
    res.send('loading...');
  },
};
