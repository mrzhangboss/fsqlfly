import request from 'umi-request';

export function queryCountInfo() {
  return request('/api/count');
}
