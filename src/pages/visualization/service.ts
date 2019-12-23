import request from '@/utils/request';

export async function queryTables() {
  return request(' /api/tables');
}

export async function queryTable({ params }: any) {
  //@ts-ignore
  return request(`/api/table/${params.table}`, { params: params });
}
