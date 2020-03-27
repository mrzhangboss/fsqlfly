import { LazyLog, ScrollFollow } from 'react-lazylog';
import { Button } from 'antd';
import { RedoOutlined } from '@ant-design/icons';
import React, { PureComponent } from 'react';

interface State {
  url: string;
  disable: boolean;
}

const realUrl = '/api/log';

const getFullUrl = (path: string) => {
  return document.location.origin + path;
};

class LastestLog extends PureComponent<State> {
  state: State = {
    url: getFullUrl(realUrl),
    disable: false,
  };

  refreshScroll = () => {
    const url = getFullUrl('/api/blank');
    this.setState({ url: url, disable: true });
    setTimeout(() => this.setState({ url: getFullUrl(realUrl), disable: false }), 100);
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

export default LastestLog;
