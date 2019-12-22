import React, { Component, ReactNode } from 'react';
import { Card, Tabs } from 'antd';
import { connect } from 'dva';
import { Dispatch } from 'redux';

interface ResultProp {
  loading: boolean;
  submitting: boolean;
  tables: TableMeta[];
  dispatch: Dispatch<any>;
}

interface ResultState {
  activeKey: string;
  panes: any[];
}

@connect(
  ({
    visualization,
    loading,
  }: {
    visualization: VisualizationResult;
    loading: { effects: { [key: string]: boolean } };
  }) => ({
    tables: visualization.tables,
    loading: loading.effects['visualization/fetchTables'],
    submitting: loading.effects['visualization/submitSelectTable'],
  }),
)
class ResultBody extends Component<ResultProp, ResultState> {
  state: ResultState = {
    activeKey: '',
    panes: [
      { title: 'Tab 1', content: 'Content of Tab Pane 1', key: '1' },
      { title: 'Tab 2', content: 'Content of Tab Pane 2', key: '2' },
    ],
  };
  newTabIndex = 3;

  add = () => {
    const { panes } = this.state;
    const activeKey = `newTab${this.newTabIndex++}`;
    panes.push({ title: 'New Tab', content: 'New Tab Pane', key: activeKey });
    this.setState({ panes, activeKey });
  };

  remove = (targetKey: string) => {
    let { activeKey } = this.state;
    let lastIndex;
    this.state.panes.forEach((pane, i) => {
      if (pane.key === targetKey) {
        lastIndex = i - 1;
      }
    });
    const panes = this.state.panes.filter(pane => pane.key !== targetKey);
    if (panes.length && activeKey === targetKey) {
      if (lastIndex >= 0) {
        activeKey = panes[lastIndex].key;
      } else {
        activeKey = panes[0].key;
      }
    }
    this.setState({ panes, activeKey });
  };

  render() {
    const { loading } = this.props;

    return (
      <Card loading={loading} style={{ marginTop: 20 }}>
        <Tabs
          hideAdd
          onChange={x => this.setState({ activeKey: x })}
          activeKey={this.state.activeKey}
          type="editable-card"
          onEdit={(a, b) => this[b](a)}
        >
          {this.state.panes.map(pane => (
            <Tabs.TabPane tab={pane.title} key={pane.key}>
              {pane.content}
            </Tabs.TabPane>
          ))}
        </Tabs>
      </Card>
    );
  }
}

export default ResultBody;
