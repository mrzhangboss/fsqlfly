import { LazyLog, ScrollFollow } from 'react-lazylog';
import { Button } from 'antd';
import { RedoOutlined } from '@ant-design/icons';
import React, { PureComponent } from 'react';

interface State {
  url: string;
  disable: boolean;
}

const realUrl = 'https://runkit.io/eliperelman/streaming-endpoint/branches/master';

class LastestLog extends PureComponent<State> {
  state: State = {
    url: realUrl,
    disable: false,
  };

  getFullUrl = (path: string) => {
    return document.location.origin + path;
  };

  refreshScroll = () => {
    const url = this.getFullUrl('/api/blank');
    this.setState({ url: url, disable: true });
    setTimeout(() => this.setState({ url: realUrl, disable: false }), 100);
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
