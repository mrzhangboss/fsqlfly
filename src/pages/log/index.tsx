import { LazyLog, ScrollFollow } from 'react-lazylog';
import { Button } from 'antd';
import { RedoOutlined } from '@ant-design/icons';
import React, { Component } from 'react';
import { ConnectProps, ConnectState } from '@/models/connect';
import { CurrentUser } from '@/models/user';
import { connect } from 'dva';

export interface GlobalHeaderRightProps extends ConnectProps {
  currentUser: CurrentUser;
}
interface State {
  url: string;
  disable: boolean;
}

const realUrl = '/api/log';

class LastestLog extends Component<GlobalHeaderRightProps, State> {
  state: State = {
    url: '',
    disable: false,
  };

  getFullUrl = (path: string) => {
    const { currentUser } = this.props;
    const token =
      currentUser === undefined || currentUser.token === undefined
        ? ''
        : '?token=' + currentUser.token;
    return document.location.origin + path + token;
  };

  componentDidMount(): void {
    this.setState({ url: this.getFullUrl(realUrl) });
  }

  refreshScroll = () => {
    const url = this.getFullUrl('/api/blank');
    this.setState({ url: url, disable: true });
    setTimeout(() => this.setState({ url: this.getFullUrl(realUrl), disable: false }), 100);
  };

  render() {
    return (
      <div style={{ height: 800, width: '100%' }}>
        <div style={{ marginBottom: 10 }}>
          <Button onClick={x => this.refreshScroll()}>
            <RedoOutlined />
          </Button>
        </div>
        <ScrollFollow
          startFollowing
          render={({ onScroll, follow, startFollowing, stopFollowing }) => (
            // @ts-ignore
            <LazyLog extraLines={100} url={this.state.url} stream follow={follow} />
          )}
        />
      </div>
    );
  }
}

export default connect(({ user }: ConnectState) => ({
  currentUser: user.currentUser,
}))(LastestLog);
