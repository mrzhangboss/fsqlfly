import mockjs from 'mockjs';
import { Request, Response } from 'express';

export default {
  'GET /api/job': mockjs.mock({
    'data|5-9': [
      {
        id: '@word',
        'name|1': ['@word', '@paragraph', '@paragraph(1000)'],
        jobId: '@word',
        'status|1': ['RUNNING', 'CANCEL', 'FAIL'],
        fullName: '@paragraph(1000)',
        startTime: '2020-03-18 15:40:35',
        'endTime|1': ['2020-03-18 15:40:35', '-'],
        'duration|1': ['14天1小时42分40秒', '1小时42分40秒', '42分40秒', '40秒'],
        detailUrl: '/job',
        'tId|1': [undefined, 1],
        'url|1': [undefined, '/terminal/1'],
        'namespaceId|1': [1, 2, 3, undefined],
        'info|1': ['aasdf', 'sdfsdfsd sdfsdfl ', undefined, '@paragraph', '@paragraph(1000,5000)'],
      },
    ],
  }),
  'POST /api/job/:mode/:word': (req: Request, res: Response) => {
    res.send({
      success: true,
    });
  },
};
