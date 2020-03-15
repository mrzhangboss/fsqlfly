// import { Reducer } from 'redux';

import { AnyAction, Reducer } from 'redux';
import { EffectsCommandMap } from 'dva';

import { IDObject } from './data';
import { getAllService, createService, deleteService, updateService, runService } from './services';

type IStateType<T> = {
  list: T[];
  [key: string]: any[];
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
    run: Effect<T>;
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
  ...dependNamespces: string[]
): {
  effects: {
    submit(
      { payload, callback }: { payload: any; callback: any },
      { call, put }: { call: any; put: any },
    ): // @ts-ignore
    Generator<any, void, unknown>;
    fetch(
      { payload }: { payload: any },
      { call, put }: { call: any; put: any },
    ): // @ts-ignore
    Generator<any, void, unknown>;
    run(
      { payload, callback }: { payload: any; callback: any },
      { call }: { call: any },
    ): // @ts-ignore
    Generator<any, void, unknown>;
  };
  namespace: string;
  reducers: {
    createOne(
      state: any,
      { payload }: { payload: any },
    ): undefined | (IStateType<T> & { list: (any | T)[] });
    init(
      state: any,
      { data }: { data: any },
    ): (IStateType<T> & { list: any }) | (undefined & { list: any });
    initDependence(
      state: any,
      { data }: { data: any; name: string },
    ): (IStateType<T> & { dependence: any }) | (undefined & { dependence: any });
    deleteOne(
      state: any,
      { payload }: { payload: any },
    ): (IStateType<T> & { list: any }) | (undefined & { list: any });
    updateList(
      state: any,
      { payload }: { payload: any },
    ): (IStateType<T> & { list: any }) | (undefined & { list: any });
  };
  state: { dependence: any[]; list: any[] };
} {
  // @ts-ignore
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
        if (dependNamespces.length > 0) {
          for (var i = 0; i < dependNamespces.length; i++) {
            let name = dependNamespces[i];
            const dependence = yield call(getAllService(name), payload);
            let saveName = i === 0 ? 'dependence' : 'dependence' + i;
            yield put({
              type: 'initDependence',
              name: saveName,
              data: Array.isArray(dependence.data) ? dependence.data : [],
            });
          }
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
      *run({ payload, callback }, { call }) {
        const res = yield call(runService, { ...payload });
        setTimeout(callback, 100, res);
      },
    },
    reducers: {
      init(state, { data }) {
        return { ...state, list: data };
      },
      initDependence(state, { data, name }) {
        return { ...state, [name]: data };
      },
      createOne(state, { payload }) {
        return state === undefined ? state : { ...state, list: [payload, ...state.list] };
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
