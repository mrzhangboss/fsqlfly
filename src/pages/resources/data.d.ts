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
  name: string;
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
  transformNum: number;
}

export interface IStateType<T> {
  list: T[];
  total?: number;
  resource?: string[];
}

export interface Connection {
  id: number;
  name: string;
  type: string;
  url: string;
  info: string;
  include: string;
  exclude: string;
  connector: string;
  updateInterval: number;
  isActive: boolean;
  isLocked: boolean;
  createAt: string;
  updateAt: string;
}

export interface ResourceName {
  id: number;
  name: string;
  info: string;
  database: string;
  connectionId: number;
  schemaVersionId?: number;
  latestSchemaId?: number;
  fullName: string;
  isLocked: boolean;
  isActive: boolean;
  isLatest: boolean;
  createAt: string;
  updateAt: string;
}

export interface ResourceTemplate {
  id: number;
  name: string;
  type: 'sink' | 'source' | 'both';
  info?: string;
  config?: string;
  connectionId: number;
  resourceNameId: number;
  isSystem: boolean;
  isDefault: boolean;
  isLocked: boolean;
  fullName: string;
  schemaVersionId?: number;
  createAt: string;
  updateAt: string;
}

export interface ResourceVersion {
  id: number;
  name?: string;
  version: number;
  info?: string;
  config?: string;
  connectionId: number;
  resourceNameId: number;
  templateId: number;
  isSystem: boolean;
  isDefault: boolean;
  isLocked: boolean;
  fullName: string;
  schemaVersionId?: number;
  createAt: string;
  updateAt: string;
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
