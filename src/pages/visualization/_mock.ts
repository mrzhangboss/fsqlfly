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
    },
    {
      tableName: 'duokan.abcd2',
      name: 'abcd2',
      namespace: 'duokan',
      info: '测试表2',
      fields: fields,
    },
    {
      tableName: 'longduokan.abcd1',
      name: 'abcd1',
      namespace: 'longduokan',
      info: '测试表2',
      fields: fields,
    },
    {
      tableName: 'longduokan.abcd2',
      name: 'abcd2',
      namespace: 'longduokan',
      info: '测试表3',
      fields: fields,
    },
    {
      tableName: 'longduokan.longlongreallong1',
      name: 'longlongreallong1',
      namespace: 'longduokan',
      info: '测试表4',
      fields: fields,
    },
    {
      tableName: 'longduokan.longlongreallong2',
      name: 'longlongreallong2',
      namespace: 'longduokan',
      info: '测试表5',
      fields: fields,
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
    },
    {
      tableName: 'longduokan.longlongreallong11',
      name: 'longlongreallong11',
      namespace: 'longduokan',
      info: '测试表4',
      fields: fields,
    },
    {
      tableName: 'longduokan.longlongreallong12',
      name: 'longlongreallong12',
      namespace: 'longduokan',
      info: '测试表4',
      fields: fields,
    },
    {
      tableName: 'longduokan.longlongreallong13',
      name: 'longlongreallong13',
      namespace: 'longduokan',
      info: '测试表4',
      fields: fields,
    },
    {
      tableName: 'longduokan.longlongreallong14',
      name: 'longlongreallong14',
      namespace: 'longduokan',
      info: '测试表4',
      fields: fields,
    },
    {
      tableName: 'longduokan.longlongreallong15',
      name: 'longlongreallong15',
      namespace: 'longduokan',
      info: '测试表4',
      fields: fields,
    },
    {
      tableName:
        'longduokan.longlongreallong15longlonglonglonglongreallong15longlonglonglonglongreallong15longlonglong',
      name:
        'longlongreallong15longlonglonglonglongreallong15longlonglonglonglongreallong15longlonglong',
      namespace: 'longduokan',
      info: '测试表4',
      fields: fields,
    },
  ],
};

const simpleFields = [
  { typ: 'number', name: 'money' },
  { typ: 'number', name: 'id' },
  { typ: 'choose', name: 'name' },
  { typ: 'string', name: 'info' },
  { typ: 'datetime', name: 'create_at' },
  { typ: 'datetime', name: 'modify_at' },
];

function getSimpleTable(tabname: string) {
  return {
    typ: 'father',
    tableName: tabname,
    show: true,
    loading: false,
    tableInfo: 'father table info',
    fields: simpleFields,
    values: [
      { typ: 'number', name: 'id', value: 1 },
      { typ: 'string', name: 'name', value: '@word' },
      { typ: 'string', name: 'info', value: 'justInfo' },
      { typ: 'number', name: 'money', value: 1.23 },
      { typ: 'datetime', name: 'create_at', value: '2019-01-02 09:00:00' },
      { typ: 'datetime', name: 'modify_at', value: '2019-01-02 09:00:00' },
    ],
  };
}

const sonField = [
  { name: 'field_a', typ: 'string' },
  { name: 'field_b', typ: 'number' },
  { name: 'field_c', typ: 'choose' },
  { name: 'name', typ: 'choose' },
];

function getSonTable(tabname: string) {
  return {
    typ: 'son',
    show: true,
    tableName: tabname,
    loading: false,
    tableInfo: 'son table info',
    search: '$id = 1 ',
    limit: 500,
    values: [
      { field_a: '@word', field_b: 1, field_c: '@word', name: '@word' },
      { field_a: '@word', field_b: 2, field_c: '@word', name: '@word' },
      { field_a: '@word', field_b: 3, field_c: '@word', name: '@word' },
      { field_a: '@word', field_b: 4, field_c: '@word', name: '@word' },
    ],
    fields: sonField,
    fieldNames: sonField.map(x => x.name),
  };
}

const proxy = {
  'GET  /api/tables': { data: tables },
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
    res: { send: (arg0: { data: any }) => void },
  ) => {
    if (Math.random() > 0.5) {
      res.send({ data: mockjs.mock(getSonTable(req.params.tableName)) });
    } else {
      res.send({ data: mockjs.mock(getSonTable(req.params.tableName)) });
    }
  },
};

export default delay(proxy, 1000);
