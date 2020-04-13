import mockjs from 'mockjs';
import { Request, Response } from 'express';

export default {
  'GET /api/job': mockjs.mock({
    'data|20': [
      {
        'id|+1': 1,
        'name|1': ['@word', '@paragraph', '@paragraph(1000)'],
        jobId: '@word',
        'status|1': ['RUNNING', 'CANCELED', 'FAILED', 'FINISHED', 'SUSPENDED', 'RECONCILING'],
        fullName: '@paragraph(1000)',
        startTime: '2020-03-18 15:40:35',
        'endTime|1': ['2020-03-18 15:40:35', '-'],
        'duration|1': ['14天1小时42分40秒', '1小时42分40秒', '42分40秒', '40秒'],
        detailUrl: '/job',
        'tId|1': [undefined, 1],
        'url|1': [undefined, '/terminal/1'],
        'namespaceId|1': [1, 2, 3, undefined],
        'pt|1': ['20200314', '20200316', '20200316202003162020031620200316', null],
        'info|1': ['aasdf', 'sdfsdfsd sdfsdfl ', undefined, '@paragraph', '@paragraph(1000,5000)'],
      },
    ],
    success: true,
  }),
  'POST /api/job/:mode/:word': (req: Request, res: Response) => {
    res.send({
      success: true,
    });
  },
};
