import mockjs from 'mockjs';

export default {
  'GET  /api/count': mockjs.mock({
    'namespaceNum|1-100': 100,
    'resourceNum|1-100': 100,
    'functionNum|1-100': 100,
    'fileNum|1-100': 100,
    'transformNum|1-100': 100,
    success: true,
  }),
};
