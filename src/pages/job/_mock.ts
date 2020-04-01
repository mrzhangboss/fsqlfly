import mockjs from 'mockjs';
import { Request, Response } from 'express';

export default {
  'GET /api/job': mockjs.mock({
    'data|5-9': [
      {
        id: '@word',
        name: '@word',
        jobId: '@word',
        'status|1': ['RUNNING', 'CANCEL', 'FAIL'],
        fullName: '@paragraph',
        startTime: '2020-03-18 15:40:35',
        'endTime|1': ['2020-03-18 15:40:35', '-'],
        'duration|1': ['14天1小时42分40秒', '1小时42分40秒', '42分40秒', '40秒'],
        detailUrl: 'http://datasource:8081/#/job/93638733783c52c3d7738fa1be5d5f61/overview',
        'tId|1': [undefined, 1],
        'url|1': [undefined, '/terminal/1'],
        'namespaceId|1': [1, 2, 3, undefined],
        'info|1': ['aasdf', 'sdfsdfsd sdfsdfl ', undefined],
      },
    ],
  }),
  'POST /api/job/:mode/:word': (req: Request, res: Response) => {
    res.send({
      success: true,
    });
  },
};
