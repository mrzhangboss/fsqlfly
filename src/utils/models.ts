// import { Reducer } from 'redux';

import { IDObject } from './data';
import { getAllService, createService, deleteService, updateService, runService } from './services';
import { message } from 'antd';

type IStateType<T> = {
  list: T[];
  [key: string]: any[];
};

type JsonResult = any & { data: any[]; success: boolean };

function getListModel<T extends IDObject>(
  namespace: string,
  ...dependNamespces: string[]
): {
  effects: {
    submit(
      { payload, callback }: { payload: any; callback: any },
      { call, put }: { call: any; put: any },
    ): Generator<any, void, unknown>;
    fetch(
      { payload }: { payload: any },
      { call, put }: { call: any; put: any },
    ): Generator<any, void, unknown>;
    run(
      { payload, callback }: { payload: any; callback: any },
      { call }: { call: any },
    ): Generator<any, void, unknown>;
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
        const res: JsonResult = yield call(getAllService(namespace), payload);
        if (res !== undefined && res.success) {
          yield put({
            type: 'init',
            data: Array.isArray(res.data) ? res.data : [],
          });
        } else {
          message.error(res.msg);
        }

        if (dependNamespces.length > 0) {
          for (var i = 0; i < dependNamespces.length; i++) {
            let name = dependNamespces[i];
            const dependence: JsonResult = yield call(getAllService(name), payload);
            let saveName = i === 0 ? 'dependence' : 'dependence' + i;
            if (dependence !== undefined && dependence.success) {
              yield put({
                type: 'initDependence',
                name: saveName,
                data: Array.isArray(dependence.data) ? dependence.data : [],
              });
            } else {
              message.error(dependence.msg);
            }
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
        const res: JsonResult = yield call(actionMethod, payload);
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
      updateList(state: { list: any[] }, { payload }) {
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
      deleteOne(state: { list: any[] }, { payload }) {
        return { ...state, list: state.list.filter(x => x.id !== payload.id) };
      },
    },
  };
}

export default getListModel;
