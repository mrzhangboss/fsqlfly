// import { Reducer } from 'redux';

import { AnyAction, Reducer } from 'redux';
import { EffectsCommandMap } from 'dva';

import { IDObject } from './data';
import { getAllService, createService, deleteService, updateService } from './services';

type IStateType<T> = {
  list: T[];
  dependence?: { id: number; [key: string]: any }[];
};

// import { number } from 'prop-types';
type Effect<T> = (
  action: AnyAction,
  effects: EffectsCommandMap & {
    select: (func: (state: IStateType<T>) => T) => T;
  },
) => void;

type ModelType<T> = {
  namespace: string;
  state: IStateType<T>;
  effects: {
    fetch: Effect<T>;
    submit: Effect<T>;
  };
  reducers: {
    init: Reducer<IStateType<T>>;
    initDependence: Reducer<IStateType<T>>;
    createOne: Reducer<IStateType<T>>;
    updateList: Reducer<IStateType<T>>;
    deleteOne: Reducer<IStateType<T>>;
  };
};

function getListModel<T extends IDObject>(
  namespace: string,
  dependNamespce?: string,
): ModelType<T> {
  return {
    namespace: namespace,
    state: {
      list: [],
      dependence: [],
    },
    effects: {
      *fetch({ payload }, { call, put }) {
        const res = yield call(getAllService(namespace), payload);
        yield put({
          type: 'init',
          data: Array.isArray(res.data) ? res.data : [],
        });
        if (dependNamespce !== undefined) {
          const dependence = yield call(getAllService(dependNamespce), payload);
          yield put({
            type: 'initDependence',
            data: Array.isArray(dependence.data) ? dependence.data : [],
          });
        }
      },
      *submit({ payload, callback }, { call, put }) {
        const actionMethod =
          payload.id === undefined
            ? createService(namespace)
            : Object.keys(payload).length === 1
            ? deleteService(namespace)
            : updateService(namespace);
        const res = yield call(actionMethod, payload);
        const actionType =
          payload.id === undefined
            ? 'createOne'
            : Object.keys(payload).length === 1
            ? 'deleteOne'
            : 'updateList';
        if (res.success) {
          yield put({
            type: actionType,
            payload: res.data ? { ...payload, ...res.data } : payload,
          });
        }
        setTimeout(callback, 100, res);
      },
    },
    reducers: {
      init(state, { data }) {
        return { ...state, list: data };
      },
      initDependence(state, { data }) {
        return { ...state, dependence: data };
      },
      createOne(state, { payload }) {
        return { ...state, list: [payload, ...state.list] };
      },
      updateList(state, { payload }) {
        return {
          ...state,
          list: state.list.map(x => {
            if (x.id === payload.id) {
              return payload;
            }
            return x;
          }),
        };
      },
      deleteOne(state, { payload }) {
        return { ...state, list: state.list.filter(x => x.id !== payload.id) };
      },
    },
  };
}

export default getListModel;
