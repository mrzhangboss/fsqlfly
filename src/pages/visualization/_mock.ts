// @ts-ignore
import { delay } from 'roadhog-api-doc';
import * as mockjs from 'mockjs';

const fields = [
  { name: 'id', typ: 'number', unique: true, primary: true },
  { name: 'create_at', typ: 'timestamp', unique: false, primary: false },
  { name: 'day', typ: 'date', unique: false, primary: false },
  { name: 'phone', typ: 'int', unique: true, primary: false },
  { name: 'name', typ: 'string', unique: false, primary: false },
  { name: 'id_card', typ: 'string', unique: false, primary: false },
  { name: 'very_long_field_like_id_card', typ: 'string', unique: false, primary: false },
];
const tables = {
  data: [
    {
      tableName: 'duokan.abcd1',
      name: 'abcd1',
      namespace: 'duokan',
      info: '测试表1',
      fields: fields,
      typ: 'hive',
    },
    {
      tableName: 'duokan.abcd2',
      name: 'abcd2',
      namespace: 'duokan',
      info: '测试表2',
      fields: fields,
      typ: 'hive',
    },
    {
      tableName: 'longduokan.abcd1',
      name: 'abcd1',
      namespace: 'longduokan',
      info: '测试表2',
      fields: fields,
      typ: 'hive',
    },
    {
      tableName: 'longduokan.abcd2',
      name: 'abcd2',
      namespace: 'longduokan',
      info: '测试表3',
      fields: fields,
      typ: 'mysql',
    },
    {
      tableName: 'longduokan.longlongreallong1',
      name: 'longlongreallong1',
      namespace: 'longduokan',
      info: '测试表4',
      fields: fields,
      typ: 'mysql',
    },
    {
      tableName: 'longduokan.longlongreallong2',
      name: 'longlongreallong2',
      namespace: 'longduokan',
      info: '测试表5',
      fields: fields,
      typ: 'mysql',
    },
    {
      tableName: 'longduokan.longlongreallong3',
      name: 'longlongreallong3',
      namespace: 'longduokan',
      info: '测试表6',
      fields: fields,
    },
    {
      tableName: 'longduokan.longlongreallong4',
      name: 'longlongreallong4',
      namespace: 'longduokan',
      info: '测试表very long long long long',
      fields: fields,
      typ: 'mysql',
    },
    {
      tableName: 'longduokan.longlongreallong11',
      name: 'longlongreallong11',
      namespace: 'longduokan',
      info: '测试表4',
      fields: fields,
      typ: 'mysql',
    },
    {
      tableName: 'longduokan.longlongreallong12',
      name: 'longlongreallong12',
      namespace: 'longduokan',
      info: '测试表4',
      fields: fields,
      typ: 'mysql',
    },
    {
      tableName: 'longduokan.longlongreallong13',
      name: 'longlongreallong13',
      namespace: 'longduokan',
      info: '测试表4',
      fields: fields,
      typ: 'mysql',
    },
    {
      tableName: 'longduokan.longlongreallong14',
      name: 'longlongreallong14',
      namespace: 'longduokan',
      info: '测试表4',
      fields: fields,
      typ: 'mysql',
    },
    {
      tableName: 'longduokan.longlongreallong15',
      name: 'longlongreallong15',
      namespace: 'longduokan',
      info: '测试表4',
      fields: fields,
      typ: 'mysql',
    },
    {
      tableName:
        'longduokan.longlongreallong15longlonglonglonglongreallong15longlonglonglonglongreallong15longlonglong',
      name:
        'longlongreallong15longlonglonglonglongreallong15longlonglonglonglongreallong15longlonglong',
      namespace: 'longduokan',
      info: '测试表4',
      fields: fields,
      typ: 'kafka',
    },
  ],
};

const sonField = [
  { name: 'field_a', typ: 'string' },
  { name: 'field_b', typ: 'number' },
  { name: 'field_c', typ: 'choose' },
  { name: 'name', typ: 'choose' },
];

function getSonTable(tabname: string) {
  return {
    tableName: tabname,
    tableInfo: 'son table info',
    'typ|1': ['kafka', 'mysql', 'hive'],
    search: '$id = 1 ',
    limit: 500,
    data: [
      { field_a: '@word', 'field_b|+1': 1, field_c: '@word', name: '@word' },
      { field_a: '@word', 'field_b|+1': 2, field_c: '@word', name: '@word' },
      { field_a: '@word', 'field_b|+1': 3, field_c: '@word', name: '@word' },
      { field_a: '@word', 'field_b|+1': 4, field_c: '@word', name: '@word' },
      { field_a: '@word', 'field_b|+1': 5, field_c: '@word', name: '@word' },
      { field_a: '@word', 'field_b|+1': 6, field_c: '@word', name: '@word' },
      { field_a: '@word', 'field_b|+1': 7, field_c: '@word', name: '@word' },
    ],
    fieldNames: sonField.map(x => x.name),
  };
}
const allTableNames = [
  {
    value: 'zhejiang',
    label: 'Zhejiang',
    children: [
      {
        value: 'hangzhou',
        label: 'Hangzhou',
        children: [
          {
            value: 'xihu',
            label: 'West Lake',
          },
          {
            value: 'xiasha',
            label: 'Xia Sha',
            disabled: true,
          },
        ],
      },
    ],
  },
  {
    value: 'jiangsu',
    label: 'Jiangsu',
    children: [
      {
        value: 'nanjing',
        label: 'Nanjing',
        children: [
          {
            value: 'zhonghuamen',
            label: 'Zhong Hua men',
          },
        ],
      },
    ],
  },
];
const proxy = {
  'GET  /api/tables': { data: tables },
  'GET  /api/table_names': { data: allTableNames },
  'GET /api/table/:tableName': (
    req: { params: { tableName: string } },
    res: { send: (arg0: { data: any; code: number; msg: string }) => void },
  ) => {
    if (Math.random() > 0.1) {
      res.send({
        data: { data: tables.data.filter(x => x.tableName !== req.params.tableName) },
        code: 0,
        msg: '',
      });
    } else {
      res.send(mockjs.mock({ data: { data: null }, code: 500, msg: '@paragraph' }));
    }
  },
  'POST /api/search/:tableName': (
    req: { params: { tableName: string } },
    res: { send: (arg0: { data: any; code: number; msg: string }) => void },
  ) => {
    if (Math.random() < 0.9999) {
      res.send({ data: mockjs.mock(getSonTable(req.params.tableName)), code: 0, msg: '' });
    } else {
      res.send(mockjs.mock({ data: null, code: 500, msg: '@csentence' }));
    }
  },
};

export default delay(proxy, 1000);
