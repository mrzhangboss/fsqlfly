import { Badge, Card, Mentions, Select, Tag, AutoComplete, message } from 'antd';
import React, { PureComponent } from 'react';
import { Dispatch } from 'redux';
import { connect } from 'dva';

const { Option } = Select;

interface SearchConfig {
  search: string;
  limit: number;
  table: string | null;
}

interface SearchProps {
  loading: boolean;
  submitting: boolean;
  tables: TableMeta[];
  dispatch: Dispatch<any>;
}

interface SearchState {
  selectTable: string;
  currentTable: TableMeta | null;
  searchConfig: SearchConfig;
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
    submitting: loading.effects['visualization/submitSearch'],
  }),
)
class SearchHeader extends PureComponent<SearchProps, SearchState> {
  state: SearchState = {
    selectTable: '',
    searchConfig: { search: '', limit: -1, table: null },
    currentTable: null,
  };

  handleSelectChange = (key: string) => {
    const { tables } = this.props;
    const { searchConfig } = this.state;
    const currentTable = tables.filter(x => x.tableName == key)[0];
    this.setState({
      selectTable: key,
      currentTable,
      searchConfig: { ...searchConfig, table: currentTable.tableName },
    });
  };

  handleSearch = () => {
    message.loading('searching...');
    const { searchConfig } = this.state;
    console.log(this.state.searchConfig + '  begin....');
    const { dispatch } = this.props;
    dispatch({
      type: 'visualization/submitSearch',
      payload: { searchConfig },
    });
  };

  handleLimitChange = (limit: number) => {
    const { searchConfig, selectTable } = this.state;
    this.setState({ searchConfig: { ...searchConfig, limit } });
    if (selectTable.length > 0) {
      this.handleSearch();
    }
  };

  handleSearchChange = (search: string) => {
    const { searchConfig, selectTable } = this.state;
    if (selectTable.length > 0 && search.charAt(search.length - 1) == '\n') this.handleSearch();
    else {
      this.setState({ searchConfig: { ...searchConfig, search } });
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

  getAutoCompleteSource = () => {
    const { currentTable } = this.state;

    if (currentTable === null) return [];

    return [currentTable].map(group => (
      <AutoComplete.OptGroup key={group.tableName} label={group.tableName}>
        {group.fields.map(opt => (
          <AutoComplete.Option key={opt.name} value={opt.name}>
            {opt.name}
            <span className="certain-search-item-count">
              {opt.primary ? <Tag>{opt.typ}</Tag> : <Badge status="success">{opt.typ} </Badge>}{' '}
            </span>
          </AutoComplete.Option>
        ))}
      </AutoComplete.OptGroup>
    ));
  };

  render() {
    const { loading, tables, submitting } = this.props;
    const { searchConfig } = this.state;

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
            disabled={submitting}
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
            prefix={'$'}
            onChange={this.handleSearchChange}
            disabled={submitting}
            value={searchConfig.search}
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
            <Option value={10}>first 10</Option>
            <Option value={100}>first 100</Option>
            <Option value={5000}>first 5000</Option>
          </Select>
        </span>
      </Card>
    );
  }
}

export default SearchHeader;
