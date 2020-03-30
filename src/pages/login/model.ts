import { AnyAction, Reducer } from 'redux';
import { message } from 'antd';
import { EffectsCommandMap } from 'dva';
import { fakeAccountLogin, getFakeCaptcha } from './service';
import { getPageQuery, setAuthority } from './utils/utils';

export interface StateType {
  status?: 'ok' | 'error';
  type?: string;
  currentAuthority?: 'user' | 'guest' | 'admin';
}

export type Effect = (
  action: AnyAction,
  effects: EffectsCommandMap & { select: <T>(func: (state: StateType) => T) => T },
) => void;

export interface ModelType {
  namespace: string;
  state: StateType;
  effects: {
    login: Effect;
    getCaptcha: Effect;
  };
  reducers: {
    changeLoginStatus: Reducer<StateType>;
  };
}

const Model: ModelType = {
  namespace: 'sign',

  state: {
    status: undefined,
  },

  effects: {
    *login({ payload }, { call, put }) {
      const response = yield call(fakeAccountLogin, payload);
      yield put({
        type: 'changeLoginStatus',
        payload: response,
      });
      // Login successfully
      if (response.code === 200) {
        message.success('登录成功！');
        const params = getPageQuery();
        const redirect = params.next;
        console.log(params);
        if (redirect) {
          window.location.href = redirect.startsWith('http')
            ? redirect
            : window.location.origin + redirect;
        }
        // yield put(routerRedux.replace(redirect || '/'));
      } else {
        message.error(response.msg);
      }
    },

    *getCaptcha({ payload }, { call }) {
      yield call(getFakeCaptcha, payload);
    },
  },

  reducers: {
    changeLoginStatus(state, { payload }) {
      setAuthority(payload.currentAuthority);
      return {
        ...state,
        status: payload.status,
        type: payload.type,
      };
    },
  },
};

export default Model;
