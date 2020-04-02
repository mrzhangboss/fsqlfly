import request from '@/utils/request';

export async function query(): Promise<any> {
  return request('/api/users');
}

export async function queryCurrent(): Promise<any> {
  return request('/api/login');
}

export async function logout(): Promise<any> {
  return request('/api/logout');
}

export async function queryNotices(): Promise<any> {
  return request('/api/notices');
}
