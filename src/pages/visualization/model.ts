import { AnyAction, Reducer } from 'redux';

import { EffectsCommandMap } from 'dva';
import { queryTables } from './service';
import { message } from 'antd';

export type Effect = (
  action: AnyAction,
  effects: EffectsCommandMap & { select: <T>(func: (state: VisualizationResult) => T) => T },
) => void;

export interface ModelType {
  namespace: string;
  state: VisualizationResult;
  effects: {
    fetchTables: Effect;
    submitSearch: Effect;
    submitSelectTable: Effect;
  };
  reducers: {
    save: Reducer<VisualizationResult>;
  };
}

const Model: ModelType = {
  namespace: 'visualization',

  state: {
    tables: [],
    search: '',
    selectTable: '',
    limit: -1,
  },

  effects: {
    *fetchTables(_, { call, put }) {
      const response = yield call(queryTables);
      yield put({
        type: 'save',
        payload: { tables: response.data },
      });
    },
    *submitSearch({ payload }, { call, put }) {
      const response = yield call(queryTables);
      console.log('submitSearch ');
      console.log(response.data);
      console.log(payload);
      message.destroy();
    },
    *submitSelectTable({ payload }, { call, put }) {
      yield put({
        type: 'save',
        payload: { selectTable: payload },
      });
      const response = yield call(queryTables);
      console.log('submitSelectTable ');
      console.log(payload);
      console.log('data is ' + response.data);
    },
  },

  reducers: {
    save(state, { payload }) {
      return {
        ...state,
        ...payload,
      };
    },
  },
};

export default Model;
