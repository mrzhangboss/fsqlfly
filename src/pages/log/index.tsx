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

  refreshScroll = () => {
    const urls = document.location.href.split('/');
    const url = urls[0] + '//' + urls[2] + '/api/blank';
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
            <LazyLog
              disabled={this.state.disable}
              filterActive={this.state.disable}
              extraLines={100}
              enableSearch
              url={this.state.url}
              stream
              onScroll={onScroll}
              follow={follow}
            />
          )}
        />
      </div>
    );
  }
}

export default LastestLog;
