import { Card, Mentions, Select, Tag, message, Icon, Button } from 'antd';
import React, { PureComponent, ReactNode } from 'react';
import { Dispatch } from 'redux';
import { connect } from 'dva';
import { TableMeta, VisualizationResult } from '../data';

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

  inputDocument: ReactNode;

  handleSelectChange = (key: string) => {
    const { tables, dispatch } = this.props;
    const currentTable = tables.filter(x => x.tableName == key)[0];
    this.setState({ currentTable });
    dispatch({
      type: 'visualization/submitSelectTable',
      payload: key,
    });
  };

  doRefresh = () => {
    const { dispatch } = this.props;
    dispatch({
      type: 'visualization/fetchTables',
    });
  };

  shouldComponentUpdate(
    nextProps: Readonly<SearchProps>,
    nextState: Readonly<SearchState>,
    nextContext: any,
  ): boolean {
    const { selectTable } = this.props;
    if (nextProps.selectTable !== selectTable) {
      if (this.inputDocument !== undefined && this.inputDocument !== null) {
        // @ts-ignore
        this.inputDocument.focus();
      }
    }
    return true;
  }

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
    const { search, loading, tables, submitting, selectSubmitting, limit } = this.props;

    const generateName = (name: string, namespace: string) => {
      if (name.length < 9) {
        return (
          <>
            <span role="img" aria-label={namespace}>
              <Tag>{namespace}</Tag>
            </span>
            {name}
          </>
        );
      } else {
        return (
          <>
            <div>
              <span role="img" aria-label={namespace}>
                <Tag>{namespace}</Tag>
              </span>
            </div>
            <div>{name}</div>
          </>
        );
      }
    };
    const tableSource = tables.map(x => (
      // @ts-ignore
      <Option value={x.tableName} label={x.name}>
        {generateName(x.name, x.namespace)}
      </Option>
    ));

    return (
      <Card loading={loading}>
        <div></div>

        <div>
          <span> </span>
          <Select
            disabled={submitting || selectSubmitting}
            showSearch
            style={{ width: '15%' }}
            placeholder="select one table"
            children={tableSource}
            onChange={this.handleSelectChange}
            optionLabelProp="label"
            maxTagTextLength={64}
          />
          <span> </span>
          <Mentions
            ref={x => (this.inputDocument = x)}
            style={{ width: '70%', marginLeft: 20 }}
            children={this.getMentionChildren()}
            prefix={['$']}
            onChange={this.handleSearchChange}
            disabled={submitting}
            value={search}
          />
          <span></span>

          <Select
            disabled={submitting}
            style={{ width: '8%', marginLeft: 20 }}
            showSearch
            placeholder="Select Result"
            defaultValue={limit}
            onChange={this.handleLimitChange}
          >
            <Option value={-1}>all data</Option>
            <Option value={5000}>first 5000</Option>
            <Option value={500}>first 500</Option>
            <Option value={100}>first 100</Option>
            <Option value={10}>first 10</Option>
          </Select>

          <span style={{ marginLeft: 2 }}></span>
          <Button onClick={this.doRefresh}>
            <Icon type="reload" />
          </Button>
        </div>
      </Card>
    );
  }
}

export default SearchHeader;
