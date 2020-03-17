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

export interface ResourceInfo {
  id: number;
  name: string;
  info: string;
  namespace: string;
  isPublish: boolean;
}

export interface TransformInfo {
  id?: number;
  name: string;
  info: string;
  namespaceId: number;
  isPublish: boolean;
  isAvailable: boolean;
  createAt: string;
  updateAt: string;
  require: string;
  sql: string;
  yaml: string;
}

export interface OneColumn {
  name: string;
  id: number;
}

export interface ResourceColumn {
  id: number;
  name: string;
  namespace: string;
  namespaceId: number;
  info: string;
  avatar: string;
  disabled: boolean;
}
