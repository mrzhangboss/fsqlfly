export default {
  'GET /api/blank': (req: any, res: { send: (arg0: string) => void }) => {
    res.send('loading...');
  },
  'GET /api/log': (req: any, res: { send: (arg0: string) => void }) => {
    const data = [];
    for (var i = 0; i < 10000; i++) data.push(i.toString());
    res.send(data.join(',\n'));
  },
};
