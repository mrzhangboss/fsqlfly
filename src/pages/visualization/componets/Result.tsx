import React, { PureComponent } from 'react';
import { Dispatch } from 'redux';
import { connect } from 'dva';
import { Card, Collapse } from 'antd';

interface ResultProps {
  loading: boolean;
  submitting: boolean;
  tables: TableMeta[];
  dispatch: Dispatch<any>;
}

interface ResultState {}

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
class SearchBody extends PureComponent<ResultProps, ResultState> {
  state: ResultState = {};

  render() {
    const { loading, submitting } = this.props;
    return (
      <div style={{ marginTop: 20 }}>
        <Card loading={loading}>
          <Collapse bordered={false}>
            <Collapse.Panel header="直系" key="1" disabled={submitting}>
              Father
            </Collapse.Panel>
            <Collapse.Panel header="子系" key="2" disabled={submitting}>
              Son
            </Collapse.Panel>
            <Collapse.Panel header="相关" key="3" disabled={submitting}>
              relative
            </Collapse.Panel>
          </Collapse>
        </Card>
      </div>
    );
  }
}

export default SearchBody;
