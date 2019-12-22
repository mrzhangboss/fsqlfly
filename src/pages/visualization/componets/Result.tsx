import React, { Component, ReactNode } from 'react';
import { Dispatch } from 'redux';
import { connect } from 'dva';
import { Card, Collapse, List, Mentions, Skeleton, Tabs, Tag, Typography, Empty } from 'antd';
import { Table, Input, Button, Icon } from 'antd';
import Highlighter from 'react-highlight-words';
import { ColumnFilterItem } from 'antd/lib/table/interface';

interface ResultProps {
  loading: boolean;
  submitting: boolean;
  tables: TableMeta[];
  dispatch: Dispatch<any>;
}

interface ResultState {
  searchText: string;
  searchedColumn: string;
  allSelectedRowKeys: { [key: string]: string[] };
  displayTables: Array<{ key: string; value: string[] }>;
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
        style={{ marginTop: 5 }}
        checked={this.state.checked}
        onChange={this.handleChange}
      >
        {tableName}{' '}
      </CheckableTag>
    );
  }
}

const ALL_RELATIONS = ['father', 'son', 'other'];

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
class SearchBody extends Component<ResultProps, ResultState> {
  getInitSelectRowKeys = () => ({ father: [], son: [], other: [] });
  getInitDisplayTables = () => ALL_RELATIONS.map(x => ({ key: x, value: [] }));

  state: ResultState = {
    searchedColumn: '',
    searchText: '',
    allSelectedRowKeys: this.getInitSelectRowKeys(),
    displayTables: this.getInitDisplayTables(),
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

  getListBody = (source: Array<TableMeta>, loading: boolean, index: string) => {
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
      selectedRowKeys: this.state.allSelectedRowKeys[index],
      onChange: (selectedRowKeys: any[], selectedRows: TableMeta[]) => {
        const { allSelectedRowKeys } = this.state;
        this.setState({ allSelectedRowKeys: { ...allSelectedRowKeys, [index]: selectedRowKeys } });
      },
    };
    const showSource = this.state.displayTables.filter(x => x.key === index);
    const showTableNames = showSource.length > 0 ? showSource[0].value : [];
    const dataSource = source.filter(x => !showTableNames.includes(x.tableName));
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
  };

  getListTag = (index: string) => {
    const { displayTables } = this.state;
    const colors = { father: 'gold', son: 'blue', other: 'lime' };
    const tags = displayTables.filter(x => x.key === index);
    if (tags.length === 0) {
      return <></>;
    }
    const allTags = tags[0].value;
    // @ts-ignore
    const color = colors[index];

    return (
      <div>
        {allTags.map(x => (
          <MyTag key={index + x} handler={this.hiddenTable} tableName={x}></MyTag>
        ))}
      </div>
    );
  };

  start = () => {
    // ajax request after empty completing

    const { dispatch } = this.props;

    const displayTables = ALL_RELATIONS.map(x => ({
      key: x,
      value: this.state.allSelectedRowKeys[x].concat(
        this.state.displayTables.filter(tb => tb.key === x)[0].value.length > 0
          ? this.state.displayTables.filter(tb => tb.key === x)[0].value
          : [],
      ),
    }));
    dispatch({
      type: 'visualization/submitSearchAll',
      payload: displayTables,
    });

    setTimeout(() => {
      this.setState({
        displayTables: displayTables,
        allSelectedRowKeys: this.getInitSelectRowKeys(),
      });
    }, 100);
  };

  clearDisplay = () => {
    this.setState({
      displayTables: this.getInitDisplayTables(),
      allSelectedRowKeys: this.getInitSelectRowKeys(),
    });
  };

  render() {
    const { loading, submitting, tables } = this.props;
    const { displayTables } = this.state;
    const hasSelectedNum = ALL_RELATIONS.map(x => this.state.allSelectedRowKeys[x].length).reduce(
      (a: number, b: number) => a + b,
      0,
    );
    const hasSelected = hasSelectedNum > 0;
    const clearCanSelected =
      displayTables.map(x => x.value.length).reduce((a: number, b: number) => a + b, 0) > 0;
    return (
      <div style={{ marginTop: 20 }}>
        <Card loading={loading}>
          <div style={{ marginBottom: 16 }}>
            <Button type="primary" onClick={this.start} disabled={!hasSelected} loading={loading}>
              Show
            </Button>
            <Button
              type="danger"
              style={{ marginLeft: 8 }}
              onClick={this.clearDisplay}
              disabled={!clearCanSelected}
              loading={loading}
            >
              Clear
            </Button>
            <span style={{ marginLeft: 8 }}>
              {hasSelected ? `Selected ${hasSelectedNum} items` : ''}
            </span>
          </div>

          <Collapse bordered={false}>
            <Collapse.Panel header="直系" key="1" disabled={submitting}>
              {this.getListBody(tables, submitting, 'father')}
            </Collapse.Panel>
            <Collapse.Panel header="子系" key="2" disabled={submitting}>
              {this.getListBody(tables, submitting, 'son')}
            </Collapse.Panel>
            <Collapse.Panel header="相关" key="3" disabled={submitting}>
              {this.getListBody(tables, submitting, 'other')}
            </Collapse.Panel>
          </Collapse>
        </Card>

        <Card loading={loading} style={{ marginTop: 20 }}>
          <Tabs defaultActiveKey="1">
            <Tabs.TabPane tab="Father" key="1">
              {this.getListTag('father')}
            </Tabs.TabPane>
            <Tabs.TabPane tab="Son" key="2">
              {this.getListTag('son')}
            </Tabs.TabPane>
            <Tabs.TabPane tab="Other" key="3">
              {this.getListTag('other')}
            </Tabs.TabPane>
          </Tabs>
        </Card>
      </div>
    );
  }
}

export default SearchBody;
