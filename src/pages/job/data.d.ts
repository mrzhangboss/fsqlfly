import { Reducer } from 'redux';

export interface IStateType<T> {
  list: T[];
  total?: number;
  resource?: string[];
}

export interface Namespace {
  id?: number;
  name: string;
  info: string;
  avatar?: string;
  isAvailable: boolean;
  isPublish: boolean;
  createAt?: string;
  updateAt?: string;
}

export interface JobInfo {
  id: string;
  name: string;
  jobId: string;
  status: string;
  fullName: string;
  startTime: string;
  duration: string;
  endTime: string;
  detailUrl: string;
  tId?: number;
  namespaceId?: number;
  sql?: string;
  require?: string;
  yaml?: string;
  info?: string;
  isPublish?: boolean;
  isAvailable?: boolean;
  url?: string;
  pt: string | null;
}
