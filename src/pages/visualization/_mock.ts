import { delay } from 'roadhog-api-doc';

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

const proxy = {
  'GET  /api/tables': tables,
};

export default delay(proxy, 1000);
