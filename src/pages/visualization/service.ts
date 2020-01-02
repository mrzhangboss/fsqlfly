import request from '@/utils/request';

export async function queryTables() {
  return request(' /api/tables', { params: { _time: new Date().getTime() } });
}

export async function queryTable(table: string) {
  //@ts-ignore
  return request(`/api/table/${table}`, { params: { _time: new Date().getTime() } });
}

export async function searchTable(table: string, params: any) {
  //@ts-ignore
  return request(`/api/search/${table}`, {
    params: { _time: new Date().getTime(), ...params },
    data: params,
    method: 'POST',
  });
}
