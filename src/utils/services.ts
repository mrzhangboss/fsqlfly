import request from 'umi-request';

export function getAllService(namespace: string) {
  return (params: any) => {
    return request(`/api/${namespace}`, { params });
  };
}

export function updateService(namespace: string) {
  return (params: { id: number }) => {
    return request(`/api/${namespace}/${params.id}`, {
      method: 'POST',
      data: params,
    });
  };
}

export function createService(namespace: string) {
  return (params: { id: number }) => {
    return request(`/api/${namespace}`, {
      method: 'POST',
      data: params,
    });
  };
}

export function deleteService(namespace: string) {
  return (params: { id: number }) => {
    return request(`/api/${namespace}/${params.id}`, {
      method: 'DELETE',
      data: params,
    });
  };
}
