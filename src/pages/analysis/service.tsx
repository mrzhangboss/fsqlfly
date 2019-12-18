import request from '@/utils/request';

export async function getTableData() {
  return request('/api/tables');
}

export async function getFakeData() {
  return request('/api/fake_chart_data');
}
