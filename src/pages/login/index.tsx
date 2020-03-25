import React, { useState } from 'react';
import { Dispatch, AnyAction } from 'redux';
import { connect } from 'dva';
import { StateType } from './model';
import styles from './style.less';
import { LoginParamsType } from './service';
import LoginFrom from './components/Login';
import { Alert } from 'antd';

const { Tab, UserName, Password, Submit } = LoginFrom;
interface LoginProps {
  dispatch: Dispatch<AnyAction>;
  login: StateType;
  submitting?: boolean;
}

const LoginMessage: React.FC<{
  content: string;
}> = ({ content }) => (
  <Alert
    style={{
      marginBottom: 24,
    }}
    message={content}
    type="error"
    showIcon
  />
);

const Login: React.FC<LoginProps> = props => {
  const { login = {}, submitting } = props;
  const { status, type: loginType } = login;
  const [type, setType] = useState<string>('account');

  const handleSubmit = (values: LoginParamsType) => {
    const { dispatch } = props;
    dispatch({
      type: 'login/login',
      payload: {
        ...values,
        type,
      },
    });
  };
  return (
    <div className={styles.main}>
      <LoginFrom activeKey={type} onTabChange={setType} onSubmit={handleSubmit}>
        <Tab key="account" tab="密码登录">
          {status === 'error' && loginType === 'account' && !submitting && (
            <LoginMessage content="密码错误" />
          )}

          <Password
            name="password"
            placeholder="密码"
            rules={[
              {
                required: true,
                message: '请输入密码！',
              },
            ]}
          />
        </Tab>
        <Tab key="token" tab="token登录">
          {status === 'error' && loginType === 'mobile' && !submitting && (
            <LoginMessage content="token错误" />
          )}
          <UserName
            name="token"
            placeholder="token"
            rules={[
              {
                required: true,
                message: '请输入token！',
              },
              {
                pattern: /^[a-zA-Z0-9-]{16}$/,
                message: 'token格式错误！',
              },
            ]}
          />
        </Tab>
        <Submit loading={submitting}>登录</Submit>
      </LoginFrom>
    </div>
  );
};

export default connect(
  ({
    login,
    loading,
  }: {
    login: StateType;
    loading: {
      effects: {
        [key: string]: boolean;
      };
    };
  }) => ({
    login,
    submitting: loading.effects['login/login'],
  }),
)(Login);
