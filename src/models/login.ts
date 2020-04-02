import { Reducer, AnyAction } from 'redux';
import { EffectsCommandMap } from 'dva';
import { parse } from 'qs';
import { logout } from '@/services/user';
import { message } from 'antd';

export function getPageQuery() {
  return parse(window.location.href.split('?')[1]);
}

export type Effect = (
  action: AnyAction,
  effects: EffectsCommandMap & { select: <T>(func: (state: {}) => T) => T },
) => void;

export interface ModelType {
  namespace: string;
  state: {};
  effects: {
    logout: Effect;
  };
  reducers: {
    changeLoginStatus: Reducer<{}>;
  };
}

const Model: ModelType = {
  namespace: 'login',

  state: {
    status: undefined,
  },

  effects: {
    *logout(_, { put, call }) {
      const response = yield call(logout);
      if (response.success) {
        message.success('退出登录成功');
        if (response.url !== undefined) {
          window.location.href = response.url;
        } else {
          window.location.href = '/';
        }
      } else {
        message.error('退出登录失败 错误代码： ' + response.code);
      }
    },
  },

  reducers: {
    changeLoginStatus(state, { payload }) {
      return {
        ...state,
        status: payload.status,
        type: payload.type,
      };
    },
  },
};

export default Model;
