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
    { tableName: 'duokan.abcd1', name: 'abcd1', namespace: 'duokan', fields: fields },
    { tableName: 'duokan.abcd2', name: 'abcd2', namespace: 'duokan', fields: fields },
    { tableName: 'longduokan.abcd1', name: 'abcd1', namespace: 'longduokan', fields: fields },
    { tableName: 'longduokan.abcd2', name: 'abcd2', namespace: 'longduokan', fields: fields },
    {
      tableName: 'longduokan.longlongreallong1',
      name: 'longlongreallong1',
      namespace: 'longduokan',
      fields: fields,
    },
    {
      tableName: 'longduokan.longlongreallong2',
      name: 'longlongreallong2',
      namespace: 'longduokan',
      fields: fields,
    },
    {
      tableName: 'longduokan.longlongreallong3',
      name: 'longlongreallong3',
      namespace: 'longduokan',
      fields: fields,
    },
    {
      tableName: 'longduokan.longlongreallong4',
      name: 'longlongreallong4',
      namespace: 'longduokan',
      fields: fields,
    },
  ],
};

const proxy = {
  'GET  /api/tables': tables,
};

export default delay(proxy, 3000);
