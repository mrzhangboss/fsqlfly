import React, { Component, ReactNode } from 'react';
import { Dispatch } from 'redux';
import { connect } from 'dva';
import {
  Card,
  Collapse,
  List,
  Mentions,
  Skeleton,
  Tabs,
  Tag,
  Typography,
  Empty,
  Switch,
} from 'antd';
import { Table, Input, Button, Icon } from 'antd';
import Highlighter from 'react-highlight-words';
import { ColumnFilterItem } from 'antd/lib/table/interface';
import { PaginationConfig } from 'antd/lib/pagination';
import { ButtonType } from 'antd/lib/button/button';

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
  columns: { name: string; buttonType: string }[];
}

interface ColumnButtonProps {
  name: string;
  buttonType: ButtonType;
  handleColumnStateChange: (name: string, buttonType: string) => void;
}

const ButtonState = ['primary', 'default', 'dashed'];

class ColumnButton extends Component<ColumnButtonProps, {}> {
  onClick = (times: number) => {
    const { name, buttonType, handleColumnStateChange } = this.props;
    const index = ButtonState.indexOf(buttonType);
    const newType = ButtonState[(index + times) % 3];
    handleColumnStateChange(name, newType);
  };

  render() {
    const { name, buttonType } = this.props;
    return (
      <Button
        size="small"
        type={buttonType}
        onClick={x => this.onClick(1)}
        onDoubleClick={x => this.onClick(2)}
      >
        {name}
      </Button>
    );
  }
}

@connect(
  ({
    visualization,
    loading,
  }: {
    visualization: VisualizationResult;
    loading: { effects: { [key: string]: boolean } };
  }) => ({
    current: visualization.details.length > 0 ? visualization.details[0] : null,
    loading: loading.effects['visualization/fetchTables'],
    submitting: loading.effects['visualization/submitSelectTable'],
  }),
)
class DrawResult extends Component<ResultProps, ResultState> {
  state: ResultState = {
    selectedRowKeys: [],
    searchText: '',
    searchedColumn: '',
    paging: false,
    columns: [],
  };

  generateTableColumn = (source: TableDetail) => {
    const fields = source.fields.map((fd, index) => {
      if (fd.typ === 'number') {
        return {
          title: fd.name,
          dataIndex: fd.name,
          key: fd.name,
          sorter: (a, b) => a[fd.name] - b[fd.name],
        };
      } else if (fd.typ === 'choose') {
        // @ts-ignore
        const chooseFilter: ColumnFilterItem[] = [
          ...new Set(source.values.map(x => x[fd.name])),
        ].map(ss => ({
          text: ss,
          value: ss,
        }));
        return {
          title: fd.name,
          dataIndex: fd.name,
          key: fd.name,
          filters: chooseFilter,
          onFilter: (value: string, record: TableMeta) => record[fd.name].indexOf(value) === 0,
          sorter: (a: TableMeta, b: TableMeta) => a[fd.name].length - b[fd.name].length,
          sortDirections: ['descend'],
        };
      } else {
        return {
          title: fd.name,
          dataIndex: fd.name,
          key: fd.name,
          width: 200,
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
        columns={this.generateTableColumn(source)}
        dataSource={source.values}
        loading={source.loading}
        pagination={this.state.paging}
      />
    );
  };

  setButtonType = (name: string, buttonType: string) => {};

  render():
    | React.ReactElement<any, string | React.JSXElementConstructor<any>>
    | string
    | number
    | {}
    | React.ReactNodeArray
    | React.ReactPortal
    | boolean
    | null
    | undefined {
    const { current } = this.props;
    return (
      <Card
        title={'Current'}
        extra={
          <span>
            <a href="#">Add</a>{' '}
            <Switch
              checkedChildren={<Icon type="check" />}
              unCheckedChildren={<Icon type="close" />}
              defaultChecked={this.state.paging === 'bottom' ? true : false}
              onChange={(checked: boolean, event: MouseEvent) =>
                this.setState({ paging: checked ? 'bottom' : false })
              }
            />
          </span>
        }
      >
        {current !== null && current !== undefined && !current.loading ? (
          this.getListBody(current)
        ) : (
          <Empty />
        )}
      </Card>
    );
  }
}

export default DrawResult;
