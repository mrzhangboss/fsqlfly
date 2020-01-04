import React, { PureComponent } from 'react';
import { Dispatch } from 'redux';
import { connect } from 'dva';
import { Card, Empty, Switch, Tag, Tooltip } from 'antd';
import { Table, Icon } from 'antd';
import { ColumnFilterItem } from 'antd/lib/table/interface';
import { PaginationConfig } from 'antd/lib/pagination';
import { TableDetail, VisualizationResult } from '../data';

interface ResultProps {
  loading: boolean;
  submitting: boolean;
  current?: TableDetail;
  dispatch: Dispatch<any>;
}

interface ResultState {
  searchText: string;
  searchedColumn: string;
  selectedRowKeys: string[];
  paging: false | PaginationConfig;
  hiddenOverflow: boolean;
  columns: { name: string; buttonType: string }[];
}

@connect(
  ({
    visualization,
    loading,
  }: {
    visualization: VisualizationResult;
    loading: { effects: { [key: string]: boolean } };
  }) => ({
    current: visualization.current,
    loading: loading.effects['visualization/fetchTables'],
    submitting: loading.effects['visualization/submitSelectTable'],
  }),
)
class DrawResult extends PureComponent<ResultProps, ResultState> {
  state: ResultState = {
    selectedRowKeys: [],
    searchText: '',
    searchedColumn: '',
    //@ts-ignore
    paging: 'bottom',
    columns: [],
    hiddenOverflow: true,
  };

  currentCard: Document = document;

  generateTableColumn = (source: TableDetail) => {
    const allValue = {};
    if (!Array.isArray(source.data)) return [];
    for (let i = 0; i < source.data.length; i++) {
      const value = source.data[i];
      for (const name in value) {
        if (allValue[name] === undefined) {
          allValue[name] = new Set([value[name]]);
        } else {
          allValue[name].add(value[name]);
        }
      }
    }
    const allValueType = {};
    const chooseValueType = {};
    for (const name in allValue) {
      let numberCount = 0;
      let stringCount = 0;
      allValue[name].forEach((x: any) => {
        if (typeof x === 'string') {
          stringCount++;
        } else if (typeof x === 'number') {
          numberCount++;
        }
      });
      let vType: string = 'object';
      if (numberCount > stringCount) {
        vType = 'number';
      } else if (numberCount < stringCount) {
        vType = 'string';
      }
      allValueType[name] = vType;

      if (allValue[name].size <= 10) {
        chooseValueType[name] = 'choose';
      }
    }
    const { hiddenOverflow } = this.state;

    const fields = source.fieldNames.map((fd, index) => {
      let sorter;
      if (allValueType[fd] === 'string') {
        sorter = (a: any, b: any) =>
          a[fd] !== null && b[fd] !== null ? a[fd].length - b[fd].length : -9999999;
      } else if (allValueType[fd] == 'number') {
        sorter = (a: any, b: any) => (a[fd] !== null && b[fd] !== null ? a[fd] - b[fd] : -9999999);
      } else {
        sorter = undefined;
      }

      if (chooseValueType[fd] === 'choose') {
        // @ts-ignore
        const chooseFilter: ColumnFilterItem[] = [...allValue[fd]]
          .filter(x => x !== null)
          .map(ss => ({
            text: ss,
            value: ss,
          }));
        return {
          title: fd,
          dataIndex: fd,
          key: fd,
          filters: chooseFilter,
          onFilter: (value: string | number, record: any) =>
            value !== null && record[fd] !== null
              ? allValueType[fd] === 'string'
                ? record[fd] === value
                : record[fd] === value
              : false,
          sorter: sorter,
          sortDirections: ['descend'],
          ellipsis: hiddenOverflow,
        };
      } else if (allValueType[fd] === 'string' || allValueType[fd] === 'number') {
        return {
          title: fd,
          dataIndex: fd,
          key: fd,
          sorter: sorter,
          ellipsis: hiddenOverflow,
        };
      } else {
        return {
          title: fd,
          dataIndex: fd,
          key: fd,
          ellipsis: hiddenOverflow,
        };
      }
    });
    return fields;
  };

  getListBody = (source: TableDetail) => {
    // @ts-ignore
    return (
      <Table
        rowKey={'tableName'}
        // @ts-ignore
        columns={this.generateTableColumn(source)}
        dataSource={source.data}
        loading={source.loading}
        pagination={this.state.paging}
      />
    );
  };

  generateTitle = (current?: TableDetail) => {
    const text = current === undefined ? '' : current.fieldNames.join(' ');
    const cur = (
      <Tooltip placement="top" title={text}>
        <Icon type="home" />
      </Tooltip>
    );
    if (current === undefined) {
      return cur;
    } else {
      const typ = current.typ;
      const color = typ === 'mysql' ? 'blue' : typ === 'hive' ? 'cyan' : 'orange';
      const tag = <Tag color={color}>{current.tableName.split('.')[0]}</Tag>;
      return (
        <div>
          {cur}

          {tag}
          {current.tableName.split('.')[1]}
        </div>
      );
    }
  };

  render() {
    const { current } = this.props;
    return (
      <Card
        ref={'currentCard'}
        title={this.generateTitle(current)}
        extra={
          <span>
            <a href="#">添加</a>{' '}
            <Switch
              checkedChildren={<Icon type="check" />}
              unCheckedChildren={<Icon type="close" />}
              defaultChecked={this.state.paging === 'bottom' ? true : false}
              //@ts-ignore
              onChange={(checked: boolean, event: MouseEvent) =>
                this.setState({ paging: checked ? 'bottom' : false })
              }
            />
            <Switch
              checkedChildren="隐藏"
              unCheckedChildren="显示"
              defaultChecked={this.state.hiddenOverflow}
              onChange={(checked: boolean, event: MouseEvent) =>
                this.setState({ hiddenOverflow: checked })
              }
            />
          </span>
        }
      >
        {current !== null && current !== undefined && !current.loading && !current.isEmpty ? (
          this.getListBody(current)
        ) : (
          <Empty />
        )}
      </Card>
    );
  }
}

export default DrawResult;
