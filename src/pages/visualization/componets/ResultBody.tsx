import React, { Component, ReactNode } from 'react';
import { Card, Descriptions, Divider, Empty, Icon, Table, Tabs, Tooltip } from 'antd';
import { connect } from 'dva';
import { Dispatch } from 'redux';
import { ColumnFilterItem } from 'antd/lib/table/interface';
import { TableDetail, VisualizationResult, TableMeta } from '../data';

interface ResultProp {
  loading: boolean;
  submitting: boolean;
  tables: TableDetail[];
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
    tables: visualization.details,
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

  generateTableColumn = (source: TableDetail) => {
    const fields = source.fieldNames.map(fd => {
      return {
        title: fd,
        dataIndex: fd,
        key: fd,
      };
    });
    return fields;
  };

  getListBody = (source: TableDetail) => {
    // @ts-ignore
    return (
      <Table
        rowKey={'tableName'}
        columns={this.generateTableColumn(source)}
        dataSource={source.data}
        loading={source.loading}
      />
    );
  };

  activeTable = (tableName: string) => {
    console.log(tableName);
    const { dispatch } = this.props;
    dispatch({
      type: 'visualization/startChangeCurrentTable',
      tableName: tableName,
    });
  };

  // @ts-ignore
  generateTableDetail = (tab: TableDetail) => {
    if (!tab.show) {
      return <></>;
    } else if (tab.loading) {
      <Card
        hoverable
        onClick={x => this.activeTable(tab.tableName)}
        key={tab.tableName}
        title={tab.tableName}
        style={{ marginBottom: 24 }}
        bordered={false}
        loading={tab.loading}
      >
        <Empty />
      </Card>;
    } else {
      return (
        <Card
          hoverable
          onDoubleClick={x => this.activeTable(tab.tableName)}
          key={tab.tableName}
          title={tab.tableName}
          style={{ marginBottom: 24 }}
          bordered={false}
          loading={tab.loading}
        >
          {this.getListBody(tab)}
        </Card>
      );
    }
  };

  render() {
    const { loading, tables } = this.props;

    return (
      <Card loading={loading} style={{ marginTop: 20 }}>
        {tables.map(x => this.generateTableDetail(x))}
      </Card>
    );
  }
}

export default ResultBody;
