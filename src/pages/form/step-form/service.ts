import request from 'umi-request';

export async function fakeSubmitForm(params: any) {
  return request('/api/forms', {
    method: 'POST',
    data: params,
  });
}

export function uploadImage() {
  return request('/api/upload', {
    method: 'POST',
  });
}

export function getAllNamespace(params: any) {
  return request('/api/resources/targetModel', { params });
}

export function updateNamespace(params: { name: string }) {
  return request(`/api/resources/namespace/${params.name}`, {
    method: 'POST',
    params,
  });
}

export function createNamespace(params: { name: string }) {
  return request(`/api/resources/namespace`, {
    method: 'POST',
    params,
  });
}

export function deleteNamespace(params: { name: string }) {
  return request(`/api/resources/namespace/${params.name}`, {
    method: 'DELETE',
    params,
  });
}

export function getResourceInfo(params: any) {
  return request(`/api/transform/info`);
}

export function getTransformInfo(params: any) {
  return request(`/api/transform`);
}

export function getResourceColumns(params: { ids: string[] }) {
  return request(`/api/columns/info`, {
    params: {
      ids: params.ids,
    },
  });
}

export function updateTransform(params: { id: number }) {
  return request(`/api/transform/${params.id}`, {
    method: 'POST',
    params: { id: params.id },
    data: params,
  });
}

export function createTransform(params: any) {
  return request(`/api/transform`, {
    method: 'POST',
    data: params,
  });
}

export function debugTransform(params: any) {
  return request(`/api/transform/debug`, {
    method: 'POST',
    data: params,
  });
}

export function getDetailColumns(params: { id: number }) {
  return request(`/api/transform/${params.id}`);
}

export function runTransform(params: { id: number }) {
  return request(`/api/transform/${params.id}/run`, {
    method: 'POST',
    params: { id: params.id },
    data: params,
  });
}
