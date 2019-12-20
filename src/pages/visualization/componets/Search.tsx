import { Badge, Card, Mentions, Select, Tag, AutoComplete, message } from 'antd';
import React, { PureComponent } from 'react';
import { Dispatch } from 'redux';
import { connect } from 'dva';

const { Option } = Select;

interface SearchProps {
  loading: boolean;
  submitting: boolean;
  selectSubmitting: boolean;
  tables: TableMeta[];
  dispatch: Dispatch<any>;
  selectTable: string;
  search: string;
  limit: number;
}

interface SearchState {
  currentTable: TableMeta | null;
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
    search: visualization.search,
    selectTable: visualization.selectTable,
    limit: visualization.limit,
    loading: loading.effects['visualization/fetchTables'],
    submitting: loading.effects['visualization/submitSearch'],
    selectSubmitting: loading.effects['visualization/submitSelectTable'],
  }),
)
class SearchHeader extends PureComponent<SearchProps, SearchState> {
  state: SearchState = {
    currentTable: null,
  };

  handleSelectChange = (key: string) => {
    const { tables, dispatch } = this.props;
    const currentTable = tables.filter(x => x.tableName == key)[0];
    this.setState({ currentTable });
    dispatch({
      type: 'visualization/submitSelectTable',
      payload: key,
    });
  };

  handleSearch = () => {
    message.loading('searching...');
    const { search, limit, selectTable } = this.props;
    const searchConfig = { search, limit, selectTable };
    console.log(searchConfig + '  begin....');
    const { dispatch } = this.props;
    dispatch({
      type: 'visualization/submitSearch',
      payload: { searchConfig },
    });
  };

  handleLimitChange = (limit: number) => {
    const { dispatch, selectTable } = this.props;
    dispatch({
      type: 'visualization/save',
      payload: { limit },
    });
    if (selectTable.length > 0) {
      this.handleSearch();
    }
  };

  handleSearchChange = (search: string) => {
    const { selectTable, dispatch } = this.props;
    if (selectTable.length > 0 && search.charAt(search.length - 1) == '\n') this.handleSearch();
    else {
      dispatch({
        type: 'visualization/save',
        payload: { search },
      });
    }
  };

  getMentionChildren = () => {
    const { currentTable } = this.state;
    if (currentTable === null) return [];
    return currentTable.fields.map(fd => (
      <Mentions.Option value={fd.name} key={fd.name} style={{ minWidth: 400 }}>
        {fd.name}
        <Tag
          style={{ float: 'right' }}
          color={fd.primary ? 'gold' : fd.unique ? 'geekblue' : undefined}
        >
          {fd.typ}
        </Tag>
      </Mentions.Option>
    ));
  };

  render() {
    const { search, loading, tables, submitting, selectSubmitting } = this.props;

    const tableSource = tables.map(x => (
      // @ts-ignore
      <Option
        value={x.tableName}
        label={x.name.length > 9 ? x.name.substring(0, 9) + '...' : x.name}
      >
        <span role="img" aria-label={x.namespace}>
          <Tag>{x.namespace}</Tag>
        </span>
        {x.name}
      </Option>
    ));

    return (
      <Card loading={loading}>
        <span>
          <Select
            disabled={submitting || selectSubmitting}
            showSearch
            style={{ width: '15%' }}
            placeholder="select one table"
            children={tableSource}
            onChange={this.handleSelectChange}
            optionLabelProp="label"
          />
          <span> </span>

          <Mentions
            style={{ width: '70%', marginLeft: 20 }}
            children={this.getMentionChildren()}
            prefix={['$']}
            onChange={this.handleSearchChange}
            disabled={submitting}
            value={search}
          />
          <span> </span>

          <Select
            disabled={submitting}
            style={{ width: '8%', marginLeft: 20 }}
            showSearch
            placeholder="Select Result"
            defaultValue={-1}
            onChange={this.handleLimitChange}
          >
            <Option value={-1}>all data</Option>
            <Option value={5000}>first 5000</Option>
            <Option value={500}>first 500</Option>
            <Option value={100}>first 100</Option>
            <Option value={10}>first 10</Option>
          </Select>
        </span>
      </Card>
    );
  }
}

export default SearchHeader;
