import request from '@/utils/request';

export async function queryTables() {
  return request(' /api/tables');
}
