import { AnyAction, Reducer } from 'redux';
import { EffectsCommandMap } from 'dva';

export interface Namespace {
  id: number;
  name: string;
  info: string;
  typ?: string;
  avatar?: string;
  isAvailable: boolean;
  isPublish: boolean;
  createAt?: string;
  updateAt?: string;
}

export interface FileResource {
  id: number;
  uniqueName: string;
  info: string;
  realPath: string;
  isPublish: boolean;
  isAvailable: boolean;
  createAt?: string;
  updateAt?: string;
}

export interface Resource {
  id?: number;
  name: string;
  info: string;
  typ: string;
  yaml: string;
  namespaceId: number;
  isPublish: boolean;
  isAvailable: boolean;
  createAt?: string;
  updateAt?: string;
}

export interface User {
  name: string;
  id: number;
}

export interface Functions {
  id?: number;
  name: string;
  functionFrom: string;
  className: string;
  constructorConfig: string;
  resourceId: number;
  isPublish: boolean;
  isAvailable: boolean;
  createAt?: string;
  updateAt?: string;
}

export interface CountPage {
  namespaceNum: number;
  resourceNum: number;
  functionNum: number;
  fileNum: number;
}

export interface IStateType<T> {
  list: T[];
  total?: number;
  resource?: string[];
}

export interface Connection {
  id: number;
  name: string;
  url: string;
  typ: string;
  suffix: string;
  username: string;
  password: string;
  info: string;
  tableRegex: string;
  tableExcludeRegex: string;
  updateInterval: number;
  isPublish: boolean;
  isAvailable: boolean;
  createAt?: string;
  updateAt?: string;
}

export interface Relationship {
  id: number;
  name: string;
  info: string;
  config: string;
  updateInterval: number;
  isPublish: boolean;
  isAvailable: boolean;
  createAt?: string;
  updateAt?: string;
}
