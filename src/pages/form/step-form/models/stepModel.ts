import {
  getResourceInfo,
  updateTransform,
  createTransform,
  debugTransform,
  getDetailColumns,
  runTransform,
} from '../service';
import { Reducer } from 'redux';
import { EffectsCommandMap } from 'dva';
import { AnyAction } from 'redux';
import { ResourceInfo, TransformInfo, ResourceColumn } from '../data';
import { Subscription } from 'dva';
import { Action, Location } from 'history';

export interface IStateType {
  current?: string;
  ready: boolean;
  step?: Partial<ResourceInfo>;
  info?: Partial<TransformInfo>;
  namespaces: { name: string; id: number }[];
  targetKeys: number[];
  resourceColumns: ResourceColumn[];
  detailColumns: ResourceColumn[];
  detail?: TransformInfo;
}

export type Effect = (
  action: AnyAction,
  effects: EffectsCommandMap & {
    select: <T>(func: (state: IStateType) => T) => T;
  },
) => void;

export interface ModelType {
  namespace: string;
  state: IStateType;
  effects: {
    submitStepForm: Effect;
    initSource: Effect;
    initSourceColumn: Effect;
    submitTransformTable: Effect;
    submitDebugTransformTable: Effect;
    initStepFromList: Effect;
    runCurrentTransform: Effect;
  };
  reducers: {
    updateLoading: Reducer<IStateType>;
    saveStepFormData: Reducer<IStateType>;
    saveCurrentStep: Reducer<IStateType>;
    sourceTableInit: Reducer<IStateType>;
    updateTarget: Reducer<IStateType>;
    updateColumnDetail: Reducer<IStateType>;
    deleteColumnTable: Reducer<IStateType>;
    updateColumnTable: Reducer<IStateType>;
    clearForm: Reducer<IStateType>;
  };
  subscriptions: { setup: Subscription };
}

const StepModel: ModelType = {
  namespace: 'formStepForm',

  state: {
    current: 'list',
    namespaces: [],
    targetKeys: [],
    resourceColumns: [],
    detailColumns: [],
    ready: false,
  },

  effects: {
    *initStepFromList({ payload }, { call, put }) {
      const res = yield call(getDetailColumns, payload);
      yield put({
        type: 'updateColumnDetail',
        payload: res.data.resources.columns,
      });
      yield put({
        type: 'saveStepFormData',
        payload: { ...payload, ...res.data.detail },
      });
      yield put({
        type: 'saveCurrentStep',
        payload: 'result',
      });
    },
    *initSource({}, { call, put }) {
      const res = yield call(getResourceInfo);
      yield put({
        type: 'sourceTableInit',
        payload: res.data,
      });
      yield put({
        type: 'updateLoading',
        ready: true,
      });
    },
    *initSourceColumn({}, { put, select }) {
      // @ts-ignore
      const ids = yield select(x => x.formStepForm.targetKeys);
      // @ts-ignore
      const useColumns = yield select(x => x.formStepForm.detailColumns);
      // @ts-ignore
      const allColumns = yield select(x => x.formStepForm.resourceColumns);
      const oldUsed = useColumns.filter((x: ResourceColumn) => ids.indexOf(x.id) >= 0);
      const oldUsedIds = oldUsed.map((x: ResourceColumn) => x.id);
      const newAdded = allColumns.filter(
        (x: ResourceColumn) => ids.indexOf(x.id) >= 0 && oldUsedIds.indexOf(x.id) < 0,
      );
      const newUseColumns = [...oldUsed, ...newAdded];
      yield put({
        type: 'updateColumnDetail',
        payload: newUseColumns,
      });
    },
    *submitStepForm({ payload }, { call, put }) {
      yield put({
        type: 'saveStepFormData',
        payload,
      });
      yield put({
        type: 'saveCurrentStep',
        payload: 'result',
      });
    },
    *submitTransformTable({ payload, callback }, { call, put, select }) {
      const action = payload.id === undefined ? createTransform : updateTransform;
      // @ts-ignore
      const columns = yield select(x => x.formStepForm.detailColumns);
      const res = yield call(action, { ...payload, columns });
      if (res.success) {
        const newTrans = {
          ...payload,
          ...res.data,
        };

        yield put({
          type: 'transform/' + (action === updateTransform ? 'updateList' : 'createOne'),
          payload: newTrans,
        });
        yield put({
          type: 'clearForm',
        });
      }
      setTimeout(callback, 100, res);
    },
    *submitDebugTransformTable({ payload, callback }, { call, put, select }) {
      const action = debugTransform;
      // @ts-ignore
      const columns = yield select(x => x.formStepForm.detailColumns);
      const res = yield call(action, { ...payload, columns });

      setTimeout(callback, 100, res);
    },
    *runCurrentTransform({ payload, callback }, { call }) {
      const res = yield call(runTransform, { ...payload });
      setTimeout(callback, 100, res);
    },
  },

  reducers: {
    updateLoading(state, { ready }) {
      return {
        ...state,
        ready: ready,
      };
    },
    updateTarget(state, { payload }) {
      return {
        ...state,
        targetKeys: payload,
      };
    },
    clearForm(state, {}) {
      return {
        ...state,
        targetKeys: [],
        detail: undefined,
      };
    },
    updateColumnDetail(state, { payload }) {
      return {
        ...state,
        detailColumns: payload,
        targetKeys: payload.map((x: ResourceColumn) => x.id),
      };
    },
    saveCurrentStep(state, { payload }) {
      return {
        ...state,
        current: payload,
      };
    },
    sourceTableInit(state, { payload }) {
      return {
        ...state,
        resourceColumns: payload.columns,
        namespaces: payload.namespaces,
      };
    },
    saveStepFormData(state, { payload }) {
      return {
        ...state,
        detail: payload,
      };
    },
    deleteColumnTable(state, { id }) {
      return {
        ...state,
        detailColumns: state.detailColumns.filter((x: ResourceColumn) => x.id !== id),
        targetKeys: state.targetKeys.filter((x: number) => id !== x),
      };
    },
    updateColumnTable(state, { payload }) {
      return {
        ...state,
        detailColumns: state.detailColumns.map((x: ResourceColumn) => {
          if (x.id === payload.id) {
            return { ...x, ...payload };
          }
          return x;
        }),
      };
    },
  },
  subscriptions: {
    setup({ history, dispatch }) {
      history.listen((location: Location, action: Action) => {
        if (location.pathname === '/transform') {
          dispatch({
            type: 'initSource',
          });
          dispatch({
            type: 'transform/fetch',
          });
        }
      });
    },
  },
};

export default StepModel;
