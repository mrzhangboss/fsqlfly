import { query as queryUsers, queryCurrent } from '@/services/user';
import { Effect } from 'dva';
import { Reducer } from 'redux';

export interface CurrentUser {
  code?: number;
  avatar?: string;
  name?: string;
  title?: string;
  group?: string;
  signature?: string;
  geographic?: any;
  tags?: {
    key: string;
    label: string;
  }[];
  unreadCount?: number;
}

export interface UserModelState {
  currentUser?: CurrentUser;
}

export interface UserModelType {
  namespace: 'user';
  state: UserModelState;
  effects: {
    fetch: Effect;
    checkLogin: Effect;
    fetchCurrent: Effect;
  };
  reducers: {
    saveCurrentUser: Reducer<UserModelState>;
    changeNotifyCount: Reducer<UserModelState>;
  };
  subscriptions: {
    setup: Reducer;
  };
}

const UserModel: UserModelType = {
  namespace: 'user',

  state: {
    currentUser: {},
  },

  effects: {
    *fetch(_, { call, put }) {
      const response = yield call(queryUsers);
      yield put({
        type: 'save',
        payload: response,
      });
    },
    *fetchCurrent(_, { call, put }) {
      const response = yield call(queryCurrent);
      yield put({
        type: 'saveCurrentUser',
        payload: response,
      });
    },
    *checkLogin(_, { call, put, select }) {
      const { currentUser } = yield select((x: { user: UserModelState }) => x.user);
      if (currentUser.code === 500) {
        window.location.href = '/admin/login?next=/static/index.html';
      }
    },
  },

  reducers: {
    saveCurrentUser(state, action) {
      return {
        ...state,
        currentUser: action.payload || {},
      };
    },
    changeNotifyCount(
      state = {
        currentUser: {},
      },
      action,
    ) {
      return {
        ...state,
        currentUser: {
          ...state.currentUser,
          notifyCount: action.payload.totalCount,
          unreadCount: action.payload.unreadCount,
        },
      };
    },
  },
  subscriptions: {
    setup({ dispatch, history, select }) {
      return history.listen(({ pathname, query }: { pathname: string; query: string }) => {
        // 进入 '/home' 路由，发起一个名叫 'query' 的 effect
        if (pathname !== '/admin/login') {
          dispatch({
            type: 'checkLogin',
          });
        }
      });
    },
  },
};

export default UserModel;
