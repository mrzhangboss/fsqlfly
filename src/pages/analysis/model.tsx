import { AnyAction, Reducer } from 'redux';

import { EffectsCommandMap } from 'dva';
import { AnalysisData } from './data.d';
import { getTableData, getFakeData } from './service';

export type Effect = (
  action: AnyAction,
  effects: EffectsCommandMap & { select: <T>(func: (state: AnalysisData) => T) => T },
) => void;

export interface ModelType {
  namespace: string;
  state: AnalysisData;
  effects: {
    fetch: Effect;
    fetchTable: Effect;
    fetchSalesData: Effect;
  };
  reducers: {
    save: Reducer<AnalysisData>;
    clear: Reducer<AnalysisData>;
  };
}

const initState = {
  visitData: [],
  visitData2: [],
  salesData: [],
  searchData: [],
  offlineData: [],
  offlineChartData: [],
  salesTypeData: [],
  salesTypeDataOnline: [],
  salesTypeDataOffline: [],
  radarData: [],
  tables: [],
};

const Model: ModelType = {
  namespace: 'analysis',

  state: initState,

  effects: {
    *fetch(_, { call, put }) {
      const response = yield call(getFakeData);
      yield put({
        type: 'save',
        payload: response,
      });
    },
    *fetchTable(_, { call, put }) {
      const response = yield call(getTableData);
      yield put({
        type: 'save',
        payload: { tables: response.data },
      });
    },
    *fetchSalesData(_, { call, put }) {
      const response = yield call(getTableData);
      yield put({
        type: 'save',
        payload: {
          salesData: response.salesData,
        },
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
    clear() {
      return initState;
    },
  },
};

export default Model;
