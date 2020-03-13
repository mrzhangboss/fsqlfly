import { ReloadOutlined } from '@ant-design/icons';
import { Card, Mentions, Select, Tag, message, Button, Modal, Cascader } from 'antd';
import React, { Component, ReactNode } from 'react';
import { Dispatch } from 'redux';
import { connect } from 'dva';
import { TableMeta, VisualizationResult } from '../data';
import styles from '@/pages/resources/style.less';
import Result from '@/pages/form/step-form/components/Result';
import { CascaderOptionType, FilledFieldNamesType } from 'antd/lib/cascader';

const { Option } = Select;

interface SearchProps {
  loading: boolean;
  submitting: boolean;
  selectSubmitting: boolean;
  tables: TableMeta[];
  tableNames: CascaderOptionType[];
  dispatch: Dispatch<any>;
  selectTable: string[];
  search: string;
  limit: number;
  errorDisplay: boolean;
  errorMsg: string;
  errorCode: number;
}

interface SearchState {
  currentTable: TableMeta | null;
  currentPrefix?: string;
}

const mapMentionFunc = (x: string) => (
  <Mentions.Option value={x} key={x} style={{ minWidth: 400 }}>
    {x}
  </Mentions.Option>
);
const dbSupportMode = ['* fields = a,b,c */', '* offset = 10 */'].map(mapMentionFunc);
const kafkaSupportMode = ['* mode = latest | earliest */', '* fields = a,b,c */'].map(
  mapMentionFunc,
);
const supportMode = {
  kafka: kafkaSupportMode,
  mysql: dbSupportMode,
  hive: dbSupportMode,
};

@connect(
  ({
    visualization,
    loading,
  }: {
    visualization: VisualizationResult;
    loading: { effects: { [key: string]: boolean } };
  }) => ({
    tables: visualization.tables,
    tableNames: visualization.tableNames,
    search: visualization.search,
    selectTable: visualization.selectTable,
    errorCode: visualization.errorCode,
    errorMsg: visualization.errorMsg,
    errorDisplay: visualization.errorDisplay,
    limit: visualization.limit,
    loading: loading.effects['visualization/fetchTables'],
    submitting: loading.effects['visualization/submitSearch'],
    selectSubmitting: loading.effects['visualization/submitSelectTable'],
  }),
)
class SearchHeader extends Component<SearchProps, SearchState> {
  state: SearchState = {
    currentTable: null,
  };

  inputDocument: ReactNode = document;
  currentSupport = supportMode['mysql'];

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
      type: 'visualization/doRefresh',
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

  handleMentionSearch = (text: string, prefix: string) => {
    this.setState({ currentPrefix: prefix });
  };

  getMentionChildren = () => {
    const { currentTable, currentPrefix } = this.state;
    if (currentTable === null) return [];
    if (currentPrefix === '=') {
      return (
        <Mentions.Option value={'='} key={'='} style={{ minWidth: 400 }}>
          {'='}
        </Mentions.Option>
      );
    } else if (currentPrefix === '/') {
      return this.currentSupport;
    }
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

  hiddenError = () => {
    const { dispatch } = this.props;
    dispatch({
      type: 'visualization/save',
      payload: {
        errorDisplay: false,
        errorCode: 0,
        errorMsg: '',
      },
    });
  };

  filterSelect = (inputValue: string, path: CascaderOptionType[], names: FilledFieldNamesType) => {
    return path.some(
      (option: any) => option.label.toLowerCase().indexOf(inputValue.toLowerCase()) > -1,
    );
  };

  onSelectChange = (value: string[], selectedOptions?: CascaderOptionType[]) => {
    console.log(value);
    console.log(selectedOptions);
    const { tables, dispatch } = this.props;
    const key = value[1] + '.' + value[2];
    const currentTable = tables.filter(x => x.tableName == key)[0];
    this.setState({ currentTable });
    dispatch({
      type: 'visualization/submitSelectTable',
      payload: value,
    });
  };

  render() {
    const {
      search,
      loading,
      tables,
      tableNames,
      submitting,
      selectSubmitting,
      limit,
      errorCode,
      errorDisplay,
      errorMsg,
      selectTable,
    } = this.props;
    const realTableName = selectTable.length === 3 ? selectTable.slice(1, 3).join('.') : '';
    const currentTables = tables.filter(x => x.tableName === realTableName);
    const currentPrefix =
      currentTables.length > 0
        ? currentTables[0].typ === 'kafka' &&
          !['>', '<', '='].includes(search.charAt(search.length - 2))
          ? ['$', '=', '/']
          : ['$', '/']
        : [];
    this.currentSupport =
      currentTables.length > 0 ? supportMode[currentTables[0].typ] : this.currentSupport;

    return (
      <>
        <Card loading={loading} style={{ borderRadius: 10 }}>
          <div></div>

          <div>
            <span> </span>
            <Cascader
              options={tableNames}
              onChange={this.onSelectChange}
              placeholder="Please select"
              showSearch={{ filter: this.filterSelect }}
              value={selectTable}
              disabled={submitting || selectSubmitting}
            />
            <span> </span>
            <Mentions
              ref={x => (this.inputDocument = x)}
              style={{ width: '70%', marginLeft: 20 }}
              children={this.getMentionChildren()}
              prefix={currentPrefix}
              onChange={this.handleSearchChange}
              onSearch={this.handleMentionSearch}
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
              <ReloadOutlined />
            </Button>
          </div>
        </Card>
        <Modal
          title={`运行结果`}
          className={styles.standardListForm}
          width={1080}
          bodyStyle={{ padding: '72px 0' }}
          destroyOnClose
          visible={errorDisplay}
          onCancel={_ => this.hiddenError()}
          footer={null}
          confirmLoading={errorDisplay}
        >
          <Result
            type={'error'}
            title={`运行失败 ${errorCode}`}
            errorInfo={errorMsg}
            actions={
              <Button type="primary" onClick={x => this.hiddenError()}>
                知道了
              </Button>
            }
            className={styles.formResult}
          />
        </Modal>
      </>
    );
  }
}

export default SearchHeader;
