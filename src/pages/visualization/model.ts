import { AnyAction, Reducer } from 'redux';

import { EffectsCommandMap } from 'dva';
import { queryTables, queryTable } from './service';
import { message } from 'antd';

export type Effect = (
  action: AnyAction,
  effects: EffectsCommandMap & {
    select: <T>(func: (state: { visualization: VisualizationResult }) => T) => T;
  },
) => void;

export interface ModelType {
  namespace: string;
  state: VisualizationResult;
  effects: {
    fetchTables: Effect;
    submitSearch: Effect;
    submitSelectTable: Effect;
    submitSearchAll: Effect;
    submitSearchOne: Effect;
    hiddenTableDetail: Effect;
  };
  reducers: {
    save: Reducer<VisualizationResult>;
    saveTableSearch: Reducer<VisualizationResult, { payload: TableDetail; type: string }>;
  };
}

// @ts-ignore
const Model: ModelType = {
  namespace: 'visualization',

  state: {
    tables: [],
    details: [],
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
    *hiddenTableDetail({ payload }, { call, put, select }) {
      const tableName = payload.tableName;
      const tables = yield select(x =>
        x.visualization.details.filter(tb => tb.tableName == tableName),
      );
      for (let x = 0; x < tables.length; x++) {
        const tb = tables[x];
        const newTb = { ...tb, show: payload.check };
        yield put({
          type: 'saveTableSearch',
          payload: newTb,
        });
      }
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
    *submitSearchAll({ payload }, { call, put, select }) {
      console.log('submitSearchAll', payload);
      // @ts-ignore
      const { selectTable } = yield select(x => x.visualization);
      for (let x = 0; x < payload.length; x++) {
        console.log('payload');
        console.log(payload[x].value);
        for (let j = 0; j < payload[x].value.length; j++) {
          const v = payload[x].value[j];
          console.log('put saveTableSearch' + v);
          yield put({
            type: 'saveTableSearch',
            payload: { tableName: v, type: payload[x].key, loading: true, show: true },
          });
          yield put({
            type: 'submitSearchOne',
            payload: { params: { selectTable, table: v } },
          });
        }
      }
    },

    *submitSearchOne({ payload }, { call, put }) {
      const response = yield call(queryTable, payload);
      yield put({
        type: 'saveTableSearch',
        payload: response.data,
      });
    },
  },

  reducers: {
    save(state, { payload }) {
      return {
        ...state,
        ...payload,
      };
    },
    //@ts-ignore
    saveTableSearch(state, { payload }) {
      if (state.details.filter(x => x.tableName === payload.tableName).length === 0) {
        const newDetail = [...state.details, payload];
        return { ...state, details: newDetail };
      } else {
        const newDetails = state.details.map(x => {
          if (x.tableName === payload.tableName) return payload;
          return x;
        });
        return {
          ...state,
          details: newDetails,
        };
      }
    },
  },
};

export default Model;
