import React, { Component } from 'react';
import { PageHeader } from 'antd';
import { Card, Col, Row } from 'antd';
import styles from './index.css';
import { connect } from 'dva';
import { CountPage } from './data';
import { Dispatch } from 'redux';

interface CountPro {
  count: CountPage;
  dispatch: Dispatch<any>;
}

@connect(({ countPage }: { countPage: CountPage }) => ({ count: countPage }))
class Welcome extends Component<CountPro> {
  componentDidMount() {
    const { dispatch } = this.props;
    dispatch({
      type: 'countPage/fetch',
    });
  }

  render() {
    const { count } = this.props;
    return (
      <>
        <PageHeader onBack={() => null} title="资源统计" subTitle="数据大屏" />
        <div className={styles.baseInfo}>
          <Row gutter={16}>
            <Col span={6}>
              <Card title="命名空间" bordered={false}>
                {count.namespaceNum}
              </Card>
            </Col>
            <Col span={6}>
              <Card title="数据源" bordered={false}>
                {count.resourceNum}
              </Card>
            </Col>
            <Col span={6}>
              <Card title="函数" bordered={false}>
                {count.functionNum}
              </Card>
            </Col>
            <Col span={6}>
              <Card title="SQL" bordered={false}>
                {count.transformNum}
              </Card>
            </Col>
          </Row>
        </div>
      </>
    );
  }
}

export default Welcome;
