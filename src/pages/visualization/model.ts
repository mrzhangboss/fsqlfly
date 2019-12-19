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
  };
  reducers: {
    save: Reducer<VisualizationResult>;
  };
}

const Model: ModelType = {
  namespace: 'visualization',

  state: {
    tables: [],
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
      console.log(response);
      console.log(payload);
      message.destroy();
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
