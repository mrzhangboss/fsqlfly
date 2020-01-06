import request from '@/utils/request';

export async function queryTables() {
  return request(' /api/tables', { params: { _time: new Date().getTime() } });
}

export async function queryTableNames() {
  return request(' /api/table_names', { params: { _time: new Date().getTime() } });
}

export async function queryTable(tables: string[]) {
  //@ts-ignore
  const tableName = tables.length === 3 ? tables[1] + '.' + tables[2] : '';
  return request(`/api/table/${tableName}`, { params: { _time: new Date().getTime() } });
}

export async function searchTable(table: string, params: any) {
  //@ts-ignore
  return request(`/api/search/${table}`, {
    params: { _time: new Date().getTime(), ...params },
    data: params,
    method: 'POST',
  });
}
