import { Col, Dropdown, Icon, Menu, Row, Tag, Button, Checkbox, Drawer, Affix } from 'antd';
import React, { ChangeEvent, Component, KeyboardEvent, Suspense } from 'react';

import { Dispatch } from 'redux';
import { GridContent } from '@ant-design/pro-layout';
import { RadioChangeEvent } from 'antd/es/radio';
import { RangePickerValue } from 'antd/es/date-picker/interface';
import { connect } from 'dva';
import PageLoading from './components/PageLoading';
import { getTimeDistance } from './utils/utils';
import { AnalysisData } from './data.d';
import styles from './style.less';
import { Icon, Input, AutoComplete, Select, Table, Collapse, Mentions } from 'antd';
import { valid } from 'mockjs';

import ReactEcharts from 'echarts-for-react';
import { OptionProps } from 'antd/lib/select';
import { PaginationConfig } from 'antd/lib/pagination/Pagination';

const { Panel } = Collapse;
const { Option, OptGroup } = AutoComplete;
const { Search } = Input;
const MetionOption = Mentions.Option;

const IntroduceRow = React.lazy(() => import('./components/IntroduceRow'));
const SalesCard = React.lazy(() => import('./components/SalesCard'));
const TopSearch = React.lazy(() => import('./components/TopSearch'));
const ProportionSales = React.lazy(() => import('./components/ProportionSales'));
const OfflineData = React.lazy(() => import('./components/OfflineData'));

interface AnalysisProps {
  analysis: AnalysisData;
  dispatch: Dispatch<any>;
  loading: boolean;
}

interface AnalysisState {
  salesType: 'all' | 'online' | 'stores';
  currentTabKey: string;
  rangePickerValue: RangePickerValue;
  myChart: any;
  option: any;
  tables: Array<string>;
  search: string;
  selectSearch: string;
  searchKeyword: string | null;
  allowPagination: boolean;
  selectKeys: Array<string>;
  drawerVisible: boolean;
  lastPrefix: string;
  prefix: string;
}

@connect(
  ({
    analysis,
    loading,
  }: {
    analysis: any;
    loading: {
      effects: { [key: string]: boolean };
    };
  }) => ({
    analysis,
    loading: loading.effects['analysis/fetch'],
  }),
)
class Analysis extends Component<AnalysisProps, AnalysisState> {
  state: AnalysisState = {
    tables: [],
    search: '',
    drawerVisible: false,
    selectSearch: '',
    lastPrefix: '',
    prefix: '@',
    searchKeyword: '',
    selectKeys: [],
    allowPagination: true,
    myChart: null,
    option: {},
    salesType: 'all',
    currentTabKey: '',
    rangePickerValue: getTimeDistance('year'),
  };

  reqRef: number = 0;

  timeoutId: number = 0;

  tableFieldsCache: any = [];

  componentDidMount() {
    const { dispatch } = this.props;
    this.reqRef = requestAnimationFrame(() => {
      dispatch({
        type: 'analysis/fetch',
      });
      dispatch({
        type: 'analysis/fetchTable',
      });
    });
  }

  componentWillUnmount() {
    const { dispatch } = this.props;
    dispatch({
      type: 'analysis/clear',
    });
    cancelAnimationFrame(this.reqRef);
    clearTimeout(this.timeoutId);
  }

  handleChangeSalesType = (e: RadioChangeEvent) => {
    this.setState({
      salesType: e.target.value,
    });
  };

  renderTitle = (title: string) => {
    return (
      <span>
        {title}
        <a
          style={{ float: 'right' }}
          href="https://www.google.com/search?q=antd"
          target="_blank"
          rel="noopener noreferrer"
        >
          more
        </a>
      </span>
    );
  };

  handleTabChange = (key: string) => {
    this.setState({
      currentTabKey: key,
    });
  };

  renderOption = (item: { category: string; query: string; count: string }) => {
    return (
      <Option key={item.category} text={item.category}>
        <div className="global-search-item">
          <span className="global-search-item-desc">
            Found {item.query} on
            <a
              href={`https://s.taobao.com/search?q=${item.query}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {item.category}
            </a>
          </span>
          <span className="global-search-item-count">{item.count} results</span>
        </div>
      </Option>
    );
  };

  getFilterFieldName = () => {
    const { analysis } = this.props;
    const { tables, search } = this.state;
    const filterWord = ['or', 'and'];
    const keyword = /(?!')[A-Za-z_]+[A-Za-z_1-9]*$/.exec(search);
    if (keyword === null || filterWord.includes(keyword[0])) {
      if (search.length !== 0) return [];
      return analysis.tables
        .filter(x => tables.includes(x.tableName))
        .map(group => (
          <OptGroup key={group.tableName} label={this.renderTitle(group.tableName)}>
            {group.fields.map(opt => (
              <Option key={opt} value={search + opt}>
                {opt}
                {/*<span className="certain-search-item-count">{opt.count} people</span>*/}
              </Option>
            ))}
          </OptGroup>
        ));
    }
    const filterName = keyword[0];
    if (search.charAt(search.length - filterName.length - 1) == "'") return [];

    return analysis.tables
      .filter(x => tables.includes(x.tableName))
      .map(group => (
        <OptGroup key={group.tableName} label={this.renderTitle(group.tableName)}>
          {group.fields
            .filter(x => x.indexOf(filterName) >= 0)
            .map(opt => (
              <Option
                key={group.tableName + opt}
                value={search.substring(0, search.length - filterName.length) + opt}
              >
                {opt}
                {/*<span className="certain-search-item-count">{opt.count} people</span>*/}
              </Option>
            ))}
        </OptGroup>
      ));
  };

  getAllFilterFieldName = () => {
    const { analysis } = this.props;

    return analysis.tables.map(group => (
      <OptGroup key={group.tableName} label={this.renderTitle(group.tableName)}>
        {group.fields.map(opt => (
          <Option key={group.tableName + opt} value={opt}>
            {opt}
            {/*<span className="certain-search-item-count">{opt.count} people</span>*/}
          </Option>
        ))}
      </OptGroup>
    ));
  };

  autoCompleteFilterFunction = (inputValue: string, option: React.ReactElement<OptionProps>) => {
    const { searchKeyword } = this.state;
    // @ts-ignore
    return (
      searchKeyword !== null &&
      typeof option.value === 'string' &&
      option.value.indexOf(searchKeyword) >= 0
    );
  };

  handleSelectChange = (keys: Array<string>) => {
    this.setState({ tables: keys });
  };

  handleSearchChange = (key: string) => {
    this.setState({ search: key });
  };

  handleFilterChange = (key: string) => {
    const keyword = /(?!')[A-Za-z_]+[A-Za-z_1-9]*$/.exec(key);
    const filterWord = ['or', 'and'];
    let filterName;
    if (keyword === null || filterWord.includes(keyword[0])) {
      if (key.length === 0) filterName = '';
      else filterName = null;
    } else {
      filterName = keyword[0];
      if (key.charAt(key.length - filterName.length - 1) == "'") filterName = null;
    }
    this.setState({ searchKeyword: filterName });
  };

  handleSearchDatabase = () => {
    console.log('in handleSearchDatabase');
    const newOption = {
      title: {
        text: 'ECharts 入门示例' + Math.random(),
      },
      tooltip: {},
      legend: {
        data: ['销量'],
      },
      xAxis: {
        data: ['衬衫', '羊毛衫', '雪纺衫', '裤子', '高跟鞋', '袜子'],
      },
      yAxis: {},
      series: [
        {
          name: '销量',
          type: 'bar',
          data: [5, 20, 36, 10, 10, 20],
        },
      ],
    };

    this.setState({ option: newOption });
  };

  handleKeyUp = (e: KeyboardEvent) => {
    if (e.keyCode == 13 && e.ctrlKey) {
      console.log(e);
      this.handleSearchDatabase();
    }
  };

  handleRangePickerChange = (rangePickerValue: RangePickerValue) => {
    const { dispatch } = this.props;
    this.setState({
      rangePickerValue,
    });

    dispatch({
      type: 'analysis/fetchSalesData',
    });
  };

  selectDate = (type: 'today' | 'week' | 'month' | 'year') => {
    const { dispatch } = this.props;
    this.setState({
      rangePickerValue: getTimeDistance(type),
    });

    dispatch({
      type: 'analysis/fetchSalesData',
    });
  };

  isActive = (type: 'today' | 'week' | 'month' | 'year') => {
    const { rangePickerValue } = this.state;
    const value = getTimeDistance(type);
    if (!rangePickerValue[0] || !rangePickerValue[1]) {
      return '';
    }
    if (
      rangePickerValue[0].isSame(value[0], 'day') &&
      rangePickerValue[1].isSame(value[1], 'day')
    ) {
      return styles.currentDate;
    }
    return '';
  };

  getTableColumnNames = () => {
    return [
      {
        title: 'Name',
        dataIndex: 'name',
        key: 'name',
        width: 100,
        fixed: 'left',
        filters: [
          {
            text: 'Joe',
            value: 'Joe',
          },
          {
            text: 'John',
            value: 'John',
          },
        ],
        onFilter: (value: any, record: { name: string }) => record.name.indexOf(value) === 0,
      },
      {
        title: 'Other',
        children: [
          {
            title: 'Age',
            dataIndex: 'age',
            key: 'age',
            width: 150,
            sorter: (a: { age: number }, b: { age: number }) => a.age - b.age,
          },
          {
            title: 'Address',
            children: [
              {
                title: 'Street',
                dataIndex: 'street',
                key: 'street',
                width: 150,
              },
              {
                title: 'Block',
                children: [
                  {
                    title: 'Building',
                    dataIndex: 'building',
                    key: 'building',
                    width: 100,
                  },
                  {
                    title: 'Door No.',
                    dataIndex: 'number',
                    key: 'number',
                    width: 100,
                  },
                ],
              },
            ],
          },
        ],
      },
      {
        title: 'Company',
        children: [
          {
            title: 'Company Address',
            dataIndex: 'companyAddress',
            key: 'companyAddress',
            width: 200,
          },
          {
            title: 'Company Name',
            dataIndex: 'companyName',
            key: 'companyName',
          },
        ],
      },
      {
        title: 'Gender',
        dataIndex: 'gender',
        key: 'gender',
        width: 80,
        fixed: 'right',
      },
      {
        title: 'aaaaaaaaaaaaaaaaaa',
        dataIndex: 'aaaaaaaaaaaaaaaaaa',
        key: 'aaaaaaaaaaaaaaaaaa',
        width: 290,
        fixed: 'right',
      },
    ];
  };

  getTableColumns = () => {
    const data = [];
    for (let i = 0; i < 100; i++) {
      const name = i > 50 ? 'John Brown' : 'Joe BB';
      data.push({
        key: 'key ' + i,
        name: name,
        age: i + 1,
        street: 'Lake Park',
        building: 'C',
        number: 2035,
        companyAddress: 'Lake Street 42',
        companyName: 'SoftLake Co',
        gender: 'M',
        aaaaaaaaaaaaaaaaaa: 'a',
        b: i * i,
        c: i * i * i,
        d: i * i * i,
        e: i * i * i,
        f: i * i * i,
      });
    }
    return data;
  };

  handleAddToCarts = () => {
    const { selectKeys } = this.state;
    console.log(selectKeys);
  };

  handleDraw = () => {
    const { selectKeys } = this.state;
    console.log(selectKeys);
  };

  onSelectChange = (selectKeys: Array<string>) => {
    this.setState({ selectKeys });
  };

  getMentionChildren = () => {
    const { prefix, lastPrefix, tables } = this.state;
    const { analysis } = this.props;
    if (prefix === '#') {
      return analysis.tables
        .filter(x => tables.includes(x.tableName))
        .map(x => (
          <Mentions.Option value={x.tableName} key={x.tableName}>
            {x.tableName}
          </Mentions.Option>
        ));
    } else {
      const allName: Array<{ key: string; value: string; field: string; tag: string }> = [];
      analysis.tables
        .filter(
          x =>
            (lastPrefix.length === 0 && tables.includes(x.tableName)) ||
            (lastPrefix.length !== 0 && x.tableName === lastPrefix),
        )
        .forEach(tb => {
          tb.fields.forEach(fd => {
            const fullName = `${tb.tableName}.${fd}`;
            allName.push({
              key: fullName,
              value: lastPrefix.length === 0 ? fullName : fd,
              field: fd,
              tag: tb.tableName,
            });
          });
        });

      return allName.map(x => (
        <Mentions.Option value={x.value} key={x.key}>
          {lastPrefix.length === 0 && <Tag> {x.tag}</Tag>} {x.field}
        </Mentions.Option>
      ));
    }
  };

  handleMentionSearch = (text: string, prefix: string) => {
    if (this.state.prefix !== prefix) {
      this.setState({ prefix });
    }
    const { tables } = this.state;

    if (prefix === '#' && tables.includes(text)) {
      this.setState({ lastPrefix: text });
    }
  };

  handleMentionSelect = (option: OptionProps, prefix: string) => {
    if (prefix === '#') {
      this.setState({ lastPrefix: typeof option.value === 'string' ? option.value : '' });
    }
  };

  render() {
    const { rangePickerValue, salesType, currentTabKey, selectKeys } = this.state;
    const { analysis, loading } = this.props;
    const {
      visitData,
      visitData2,
      salesData,
      searchData,
      offlineData,
      offlineChartData,
      salesTypeData,
      salesTypeDataOnline,
      salesTypeDataOffline,
      tables,
    } = analysis;
    let salesPieData;
    if (salesType === 'all') {
      salesPieData = salesTypeData;
    } else {
      salesPieData = salesType === 'online' ? salesTypeDataOnline : salesTypeDataOffline;
    }
    const menu = (
      <Menu>
        <Menu.Item>操作一</Menu.Item>
        <Menu.Item>操作二</Menu.Item>
      </Menu>
    );

    const dropdownGroup = (
      <span className={styles.iconGroup}>
        <Dropdown overlay={menu} placement="bottomRight">
          <Icon type="ellipsis" />
        </Dropdown>
      </span>
    );

    const activeKey = currentTabKey || (offlineData[0] && offlineData[0].name);

    const tableSource = tables.map(x => (
      // @ts-ignore
      <Option
        value={x.tableName}
        label={x.name.length > 9 ? x.name.substring(0, 9) + '...' : x.name}
      >
        <span role="img" aria-label={x.namespace}>
          <Tag>{x.namespace}</Tag>
        </span>
        {x.tableName}
      </Option>
    ));

    const getF = () => {
      return (
        <GridContent>
          <React.Fragment>
            <Suspense fallback={<PageLoading />}>
              <IntroduceRow loading={loading} visitData={visitData} />
            </Suspense>
            <Suspense fallback={null}>
              <SalesCard
                rangePickerValue={rangePickerValue}
                salesData={salesData}
                isActive={this.isActive}
                handleRangePickerChange={this.handleRangePickerChange}
                loading={loading}
                selectDate={this.selectDate}
              />
            </Suspense>
            <Row
              gutter={24}
              type="flex"
              style={{
                marginTop: 24,
              }}
            >
              <Col xl={12} lg={24} md={24} sm={24} xs={24}>
                <Suspense fallback={null}>
                  <TopSearch
                    loading={loading}
                    visitData2={visitData2}
                    searchData={searchData}
                    dropdownGroup={dropdownGroup}
                  />
                </Suspense>
              </Col>
              <Col xl={12} lg={24} md={24} sm={24} xs={24}>
                <Suspense fallback={null}>
                  <ProportionSales
                    dropdownGroup={dropdownGroup}
                    salesType={salesType}
                    loading={loading}
                    salesPieData={salesPieData}
                    handleChangeSalesType={this.handleChangeSalesType}
                  />
                </Suspense>
              </Col>
            </Row>
            <Suspense fallback={null}>
              <OfflineData
                activeKey={activeKey}
                loading={loading}
                offlineData={offlineData}
                offlineChartData={offlineChartData}
                handleTabChange={this.handleTabChange}
              />
            </Suspense>
          </React.Fragment>
        </GridContent>
      );
    };

    const hasSelected = selectKeys.length > 0;
    const rowSelection = {
      selectKeys,
      onChange: this.onSelectChange,
    };

    return (
      <div>
        <div style={{ position: 'fixed', bottom: 30, right: 60, zIndex: 10000 }}>
          <Button
            type="primary"
            onClick={x => this.setState({ drawerVisible: true })}
            style={{ borderRadius: 360 }}
          >
            <Icon type="shopping-cart" />
          </Button>
        </div>

        <Select
          mode="multiple"
          style={{ width: '100%' }}
          placeholder="select one table"
          children={tableSource}
          onChange={this.handleSelectChange}
          optionLabelProp="label"
        />

        <span>
          <Mentions
            style={{ width: '100%' }}
            placeholder="input @ to mention field, # to mention tag"
            prefix={['@', '#']}
            children={this.getMentionChildren()}
            // onSearch={(_, p) => this.setState({ prefix: p, lastPrefix: this.state.prefix })}
            onSearch={this.handleMentionSearch}
            onKeyUp={this.handleKeyUp}
            onSelect={this.handleMentionSelect}
          />
        </span>

        <Collapse accordion>
          <Panel header="Advance Setting" key="1">
            <Select
              showSearch
              style={{ width: 200 }}
              placeholder="Select echart Type"
              defaultValue="bar"
              // onChange={onChange}
              // onFocus={onFocus}
              // onBlur={onBlur}
              // onSearch={onSearch}
            >
              <Option value="bar">bar</Option>
              <Option value="line">line</Option>
              <Option value="pie">pie</Option>
              <Option value="scatter">sc</Option>
            </Select>
            <span> </span>

            <Select
              showSearch
              style={{ width: 200 }}
              placeholder="Select Result"
              defaultValue="all"
              // onChange={onChange}
              // onFocus={onFocus}
              // onBlur={onBlur}
              // onSearch={onSearch}
            >
              <Option value="all">all data</Option>
              <Option value="10">first 10</Option>
              <Option value="100">first 100</Option>
              <Option value="5000">first 5000</Option>
            </Select>
            <span> </span>

            <Select
              showSearch
              style={{ width: 200 }}
              placeholder="Select Result"
              defaultValue="all"
              // onChange={onChange}
              // onFocus={onFocus}
              // onBlur={onBlur}
              // onSearch={onSearch}
            >
              <Option value="all">all data</Option>
              <Option value="10">first 10</Option>
              <Option value="100">first 100</Option>
              <Option value="5000">first 5000</Option>
            </Select>
            <span> </span>

            <Input
              onKeyUp={this.handleKeyUp}
              suffix={
                <Icon
                  type="search"
                  className="certain-category-icon"
                  onClick={this.handleSearchDatabase}
                />
              }
            />
          </Panel>
        </Collapse>
        <br />

        <div>
          <div className="table-operations">
            <Checkbox
              checked={this.state.allowPagination}
              onChange={x => this.setState({ allowPagination: x.target.checked })}
            >
              {this.state.allowPagination ? 'paging' : 'no paging'}
            </Checkbox>
            <Button
              type="primary"
              onClick={this.handleAddToCarts}
              disabled={!hasSelected}
              loading={loading}
            >
              Add To Carts
            </Button>
            <span> </span>

            <Button
              type="primary"
              onClick={this.handleDraw}
              disabled={!hasSelected}
              loading={loading}
            >
              Draw The Chart
            </Button>
          </div>
          <Table
            rowSelection={rowSelection}
            pagination={this.state.allowPagination ? { position: 'bottom' } : false}
            columns={this.getTableColumnNames()}
            dataSource={this.getTableColumns()}
            bordered
            size="small"
            scroll={{ x: 'calc(700px + 50%)', y: 540 }}
          />

          <Drawer
            title="Save Data"
            placement="right"
            closable={false}
            onClose={x => this.setState({ drawerVisible: false })}
            visible={this.state.drawerVisible}
          >
            <p>Some contents...</p>
            <p>Some contents...</p>
            <p>Some contents...</p>
          </Drawer>
        </div>

        <ReactEcharts
          // key={}
          option={this.state.option}
          // onEvents={onEvents}
          notMerge={true}
          lazyUpdate={true}
          style={{ height: '300px', left: '12px', top: '-8px' }}
        />

        <br />

        {getF()}
      </div>
    );
  }
}

export default Analysis;
