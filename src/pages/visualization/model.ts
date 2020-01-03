import { AnyAction, Reducer } from 'redux';

import { EffectsCommandMap } from 'dva';
import { queryTables, queryTable, searchTable } from './service';
import { message } from 'antd';
import { VisualizationResult, TableDetail } from './data';

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
    doRefresh: Effect;
    submitSearch: Effect;
    submitSelectTable: Effect;
    submitSearchAll: Effect;
    submitSearchOne: Effect;
    hiddenTableDetail: Effect;
    startChangeCurrentTable: Effect;
  };
  reducers: {
    save: Reducer<VisualizationResult>;
    saveTableSearch: Reducer<VisualizationResult, { payload: TableDetail; type: string }>;
    changeCurrentTable: Reducer<VisualizationResult, { tableName: string; type: string }>;
    deleteTable: Reducer<VisualizationResult, { tableName: string; type: string }>;
  };
}

// @ts-ignore
const Model: ModelType = {
  namespace: 'visualization',

  state: {
    tables: [],
    relatedTables: [],
    details: [],
    search: '',
    selectTable: '',
    limit: -1,
    currentDisplayTables: [],
    selectRelatedTableKeys: [],
    errorDisplay: false,
    errorCode: 0,
    errorMsg: '',
  },

  effects: {
    *fetchTables({ payload }, { call, put }) {
      const response = yield call(queryTables);
      yield put({
        type: 'save',
        payload: { tables: response.data.data },
      });
    },
    *doRefresh(_, { call, put }) {
      yield put({
        type: 'save',
        payload: {
          tables: [],
          relatedTables: [],
          details: [],
          selectTable: '',
          limit: -1,
          currentDisplayTables: [],
          selectRelatedTableKeys: [],
          errorDisplay: false,
          errorCode: 0,
          errorMsg: '',
        },
      });

      yield put({
        type: 'fetchTables',
      });
    },
    *submitSearch({ payload }, { call, put, select }) {
      const { limit, search, selectTable } = yield select(x => x.visualization);
      const response = yield call(searchTable, selectTable, { limit, search });
      if (response.code !== 0) {
        yield put({
          type: 'save',
          payload: {
            errorDisplay: true,
            errorCode: response.code,
            errorMsg: response.msg,
          },
        });
        return;
      }
      yield put({
        type: 'saveTableSearch',
        payload: response.data,
      });
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
        payload: { selectTable: payload, selectRelatedTableKeys: [] },
      });
      const response = yield call(queryTable, payload);
      yield put({
        type: 'save',
        payload: { relatedTables: Array.isArray(response.data.data) ? response.data.data : [] },
      });

      console.log('submitSelectTable ');
      console.log(payload);
      console.log('data is ' + response.data);
    },
    *submitSearchAll({ payload }, { call, put, select }) {
      console.log('submitSearchAll', payload);
      // @ts-ignore
      const { selectTable } = yield select(x => x.visualization);
      const { current } = yield select(x => x.visualization);
      if (current === undefined) {
        yield put({
          type: 'submitSearchOne',
          payload: { params: { selectTable, table: selectTable } },
        });
      }
      for (let v of payload) {
        console.log('put saveTableSearch' + v);
        yield put({
          type: 'saveTableSearch',
          payload: { tableName: v, loading: true, show: true },
        });
        yield put({
          type: 'submitSearchOne',
          payload: { params: { selectTable, table: v } },
        });
      }
    },

    *submitSearchOne({ payload }, { call, put }) {
      const response = yield call(searchTable, payload.params.table, payload.params);
      yield put({
        type: 'saveTableSearch',
        payload: { ...response.data, loading: false },
      });
    },
    *startChangeCurrentTable({ tableName }, { call, put, select }) {
      const { selectTable } = yield select(x => x.visualization);
      if (selectTable !== tableName) {
        yield put({
          type: 'submitSelectTable',
          payload: tableName,
        });
      }
      yield put({
        type: 'changeCurrentTable',
        tableName: tableName,
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
      let newState;
      if (state !== undefined && payload.tableName === state.selectTable) {
        newState = { ...state, current: payload };
      } else {
        newState = state;
      }

      if (
        newState !== undefined &&
        newState.details.filter(x => x.tableName === payload.tableName).length === 0
      ) {
        const newDetail = [...newState.details, payload];
        return { ...newState, details: newDetail };
      } else if (newState !== undefined) {
        const newDetails = newState.details.map(x => {
          if (x.tableName === payload.tableName) return payload;
          return x;
        });
        return {
          ...newState,
          details: newDetails,
        };
      }
    },
    //@ts-ignore
    changeCurrentTable(state, { tableName }) {
      if (state !== undefined) {
        const current = state.details.filter(x => x.tableName === tableName);
        if (current.length > 0) {
          const currentTable = current[0];
          return {
            ...state,
            current: currentTable,
            selectTable: currentTable.tableName,
            search: currentTable.search,
            limit: currentTable.limit,
          };
        }
      }
      return state;
    },
    // @ts-ignore
    deleteTable(state, { tableName }) {
      // @ts-ignore
      return { ...state, details: state.details.filter(x => x.tableName !== tableName) };
    },
  },
};

export default Model;
