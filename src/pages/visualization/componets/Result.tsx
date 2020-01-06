import React, { Component, ReactNode } from 'react';
import { Dispatch } from 'redux';
import { connect } from 'dva';
import { Card, Collapse, List, Tag, Empty } from 'antd';
import { Table, Input, Button, Icon } from 'antd';
// @ts-ignore
import Highlighter from 'react-highlight-words';
import { ColumnFilterItem } from 'antd/lib/table/interface';
import { TableMeta, VisualizationResult } from '../data';

interface ResultProps {
  loading: boolean;
  tableLoading: boolean;
  submitting: boolean;
  tables: TableMeta[];
  selectedRowKeys: string[];
  displayTables: string[];
  dispatch: Dispatch<any>;
}

interface ResultState {
  searchText: string;
  searchedColumn: string;
  currentTables: Array<{ name: string; show: boolean }>;
}

const { CheckableTag } = Tag;

interface TagProp {
  handler: (tb: string, check: boolean) => void;
  tableName: string;
}

class MyTag extends React.PureComponent<TagProp, { checked: boolean }> {
  state = { checked: true };

  handleChange = (checked: boolean) => {
    this.props.handler(this.props.tableName, checked);
    this.setState({ checked });
  };

  render() {
    const { tableName } = this.props;
    return (
      <CheckableTag
        style={{ marginTop: 5, borderRadius: 10 }}
        checked={this.state.checked}
        onChange={this.handleChange}
      >
        {tableName}{' '}
      </CheckableTag>
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
    tables: visualization.relatedTables,
    selectedRowKeys: visualization.selectRelatedTableKeys,
    displayTables: visualization.currentDisplayTables,
    loading: loading.effects['visualization/fetchTables'],
    tableLoading: loading.effects['visualization/submitSearchOne'],
    submitting: loading.effects['visualization/submitSelectTable'],
  }),
)
class SearchBody extends Component<ResultProps, ResultState> {
  state: ResultState = {
    searchedColumn: '',
    searchText: '',
    currentTables: [],
  };

  searchInput: ReactNode = document;

  getColumnSearchProps = (dataIndex: string) => ({
    // @ts-ignore
    filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => (
      <div style={{ padding: 8 }}>
        <Input
          ref={node => {
            this.searchInput = node;
          }}
          placeholder={`Search ${dataIndex}`}
          value={selectedKeys[0]}
          onChange={e => setSelectedKeys(e.target.value ? [e.target.value] : [])}
          onPressEnter={() => this.handleSearch(selectedKeys, confirm, dataIndex)}
          style={{ width: 188, marginBottom: 8, display: 'block' }}
        />
        <Button
          type="primary"
          onClick={() => this.handleSearch(selectedKeys, confirm, dataIndex)}
          icon="search"
          size="small"
          style={{ width: 90, marginRight: 8 }}
        >
          Search
        </Button>
        <Button onClick={() => this.handleReset(clearFilters)} size="small" style={{ width: 90 }}>
          Reset
        </Button>
      </div>
    ),
    filterIcon: (filtered: boolean) => (
      <Icon type="search" style={{ color: filtered ? '#1890ff' : undefined }} />
    ),
    onFilter: (value: string, record: { [key: string]: string }) =>
      record[dataIndex]
        .toString()
        .toLowerCase()
        .includes(value.toLowerCase()),
    onFilterDropdownVisibleChange: (visible: boolean) => {
      if (visible) {
        // @ts-ignore
        setTimeout(() => this.searchInput.select());
      }
    },
    render: (text: string) =>
      this.state.searchedColumn === dataIndex ? (
        <Highlighter
          highlightStyle={{ backgroundColor: '#ffc069', padding: 0 }}
          searchWords={[this.state.searchText]}
          autoEscape
          textToHighlight={text.toString()}
        />
      ) : (
        text
      ),
  });

  handleSearch = (selectedKeys: string[], confirm: () => void, dataIndex: string) => {
    confirm();
    this.setState({
      searchText: selectedKeys[0],
      searchedColumn: dataIndex,
    });
  };

  handleReset = (clearFilters: () => void) => {
    clearFilters();
    this.setState({ searchText: '' });
  };

  getColumnInfo = (tab: TableMeta) => {
    return (
      <List
        header={
          <div>
            <Tag>{tab.namespace}</Tag> {tab.name}
          </div>
        }
        bordered
        dataSource={tab.fields}
        renderItem={fd => (
          <List.Item>
            {fd.name}
            <Tag
              style={{ float: 'right' }}
              color={fd.primary ? 'gold' : fd.unique ? 'geekblue' : undefined}
            >
              {fd.typ}
            </Tag>
          </List.Item>
        )}
      />
    );
  };

  onSelectRowChange = (selectedRowKeys: any[], selectedRows: TableMeta[]) => {
    const { dispatch } = this.props;
    dispatch({
      type: 'visualization/save',
      payload: { selectRelatedTableKeys: selectedRowKeys },
    });
  };

  getListBody = (source: Array<TableMeta>, loading: boolean) => {
    const namespaceFilters: ColumnFilterItem[] = [...new Set(source.map(x => x.namespace))].map(
      x => ({
        text: x,
        value: x,
      }),
    );
    const columns = [
      {
        title: 'Name',
        dataIndex: 'name',
        key: 'name',
        width: '40%',
        sorter: (a: TableMeta, b: TableMeta) => a.name.length - b.name.length,
        ...this.getColumnSearchProps('name'),
      },
      {
        title: 'Namespace',
        dataIndex: 'namespace',
        key: 'namespace',
        width: '15%',
        filters: namespaceFilters,
        onFilter: (value: string, record: TableMeta) => record.namespace.indexOf(value) === 0,
        sorter: (a: TableMeta, b: TableMeta) => a.namespace.length - b.namespace.length,
        sortDirections: ['descend'],
      },
      {
        title: 'Info',
        dataIndex: 'info',
        key: 'info',
        ...this.getColumnSearchProps('info'),
      },
    ];
    const rowSelection = {
      selectedRowKeys: this.props.selectedRowKeys,
      onChange: this.onSelectRowChange,
    };
    const { displayTables } = this.props;
    const dataSource = source.filter(x => !displayTables.includes(x.tableName));
    // @ts-ignore
    return (
      <Table
        rowKey={'tableName'}
        columns={columns}
        expandedRowRender={record => this.getColumnInfo(record)}
        rowSelection={rowSelection}
        dataSource={dataSource}
        loading={loading}
        pagination={false}
      />
    );
  };

  hiddenTable = (key: string, check: boolean) => {
    console.log(key, check);
    const { dispatch } = this.props;
    dispatch({
      type: 'visualization/hiddenTableDetail',
      payload: { tableName: key, check: check },
    });
  };

  getListTag = () => {
    const { displayTables } = this.props;
    const tags = displayTables;
    if (tags.length === 0) {
      return <></>;
    }
    // @ts-ignore

    return (
      <div>
        {displayTables.map(x => (
          <MyTag key={x} handler={this.hiddenTable} tableName={x}></MyTag>
        ))}
      </div>
    );
  };

  start = () => {
    // ajax request after empty completing

    const { dispatch, selectedRowKeys } = this.props;

    console.log(selectedRowKeys);
    dispatch({
      type: 'visualization/submitSearchAll',
      payload: selectedRowKeys,
    });
  };

  render() {
    const { loading, submitting, tables, selectedRowKeys, tableLoading } = this.props;
    const hasSelectedNum = selectedRowKeys.length;
    const hasSelected = hasSelectedNum > 0;
    const clearCanSelected = hasSelectedNum > 0;
    return (
      <div style={{ marginTop: 20 }}>
        <Card loading={loading}>
          <div style={{ marginBottom: 16 }}>
            <Button type="primary" onClick={this.start} disabled={!hasSelected} loading={loading}>
              展示
            </Button>

            <span style={{ marginLeft: 8 }}>
              {hasSelected ? `Selected ${hasSelectedNum} items` : ''}
            </span>
          </div>

          <Collapse bordered={false}>
            <Collapse.Panel header="关联表" key="1" disabled={submitting}>
              {this.getListBody(tables, submitting || tableLoading)}
            </Collapse.Panel>
          </Collapse>
        </Card>

        {/*<Card loading={loading} style={{ marginTop: 20 }}>*/}
        {/*  {this.getListTag()}*/}
        {/*</Card>*/}
      </div>
    );
  }
}

export default SearchBody;
