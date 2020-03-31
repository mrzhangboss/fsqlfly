import { query as queryUsers, queryCurrent } from '@/services/user';
import { Effect } from 'dva';
import { Reducer } from 'redux';

// import router from 'umi/router';
// import { history } from 'umi';
// import { browserHistory } from 'react-router';

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
  token?: string;
}

export interface UserModelState {
  currentUser?: CurrentUser;
}

export interface UserModelType {
  namespace: 'user';
  state: UserModelState;
  effects: {
    fetch: Effect;
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
      if (response.code === undefined || response.code === 500) {
        // router.push({pathname: '/login', query: { from : ''}})
        console.log(response);

        // history.push({ pathname: '/login', query: { from: document.location.pathname } });
        const pathname = document.location.pathname;
        if (!pathname.startsWith('/login')) {
          window.location.href = '/login?next=' + encodeURI(document.location.pathname);
        }
        return;
      }
      yield put({
        type: 'saveCurrentUser',
        payload: response,
      });
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
        console.log('route in ' + pathname);
        dispatch({
          type: 'fetchCurrent',
        });
      });
    },
  },
};

export default UserModel;
