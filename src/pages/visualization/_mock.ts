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
  ],
};

const simpleTable = {
  typ: 'father',
  tableName: 'father_table',
  show: true,
  loading: false,
  tableInfo: 'father table info',
  values: [
    { typ: 'number', name: 'id', value: 1 },
    { typ: 'string', name: 'name', value: 'I am a name' },
    { typ: 'string', name: 'info', value: 'justInfo' },
    { typ: 'number', name: 'money', value: 1.23 },
    { typ: 'datetime', name: 'create_at', value: '2019-01-02 09:00:00' },
    { typ: 'datetime', name: 'modify_at', value: '2019-01-02 09:00:00' },
  ],
};

const sonTable = {
  typ: 'son',
  show: true,
  loading: false,
  tableName: 'son_table',
  tableInfo: 'son table info',
  'values|20': [{ field_a: 'field', field_b: 1, field_c: '@word', name: '@word' }],
};
const proxy = {
  'GET  /api/tables': tables,
  'GET /api/table': mockjs.mock({ 'data|1': [simpleTable, sonTable] }),
};

export default delay(proxy, 1000);
