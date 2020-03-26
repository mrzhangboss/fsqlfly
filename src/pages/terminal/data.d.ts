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

export interface TerminalInfo {
  id: string;
  name: string;
}
