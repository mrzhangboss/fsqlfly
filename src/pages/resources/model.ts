// import { Reducer } from 'redux';
import { EffectsCommandMap } from 'dva';
import { AnyAction, Reducer } from 'redux';

// import { number } from 'prop-types';
import { CountPage } from './data';
import { queryCountInfo } from './servers';

export type Effect = (
  action: AnyAction,
  effects: EffectsCommandMap & {
    select: <T>(func: (state: CountPage) => T) => T;
  },
) => void;

export interface ModelType {
  namespace: string;
  state: CountPage;
  effects: {
    fetch: Effect;
  };
  reducers: {
    update: Reducer<CountPage>;
  };
}

const Model: ModelType = {
  namespace: 'countPage',
  state: {
    namespaceNum: 0,
    resourceNum: 0,
    functionNum: 0,
    fileNum: 0,
    transformNum: 0,
  },
  effects: {
    *fetch({}, { call, put }) {
      const response = yield call(queryCountInfo);
      yield put({
        type: 'update',
        payload: response !== undefined ? response : {},
      });
    },
  },
  reducers: {
    update(state, action) {
      return {
        ...state,
        ...action.payload,
      };
    },
  },
};

export default Model;
