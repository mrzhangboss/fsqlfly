import { DingdingOutlined } from '@ant-design/icons';
import { LazyLog, ScrollFollow } from 'react-lazylog';
import { Button, Card, Steps, Result, Descriptions } from 'antd';
import { FormattedMessage, formatMessage } from 'umi-plugin-react/locale';
import React, { Fragment } from 'react';
import { GridContent } from '@ant-design/pro-layout';

import styles from './index.less';

const { Step } = Steps;

const desc1 = (
  <div className={styles.title}>
    <div style={{ margin: '8px 0 4px' }}>
      <FormattedMessage id="result-success.success.step1-operator" defaultMessage="Qu Lili" />
      <DingdingOutlined style={{ marginLeft: 8, color: '#00A0E9' }} />
    </div>
    <div>2016-12-12 12:32</div>
  </div>
);

const desc2 = (
  <div style={{ fontSize: 12 }} className={styles.title}>
    <div style={{ margin: '8px 0 4px' }}>
      <FormattedMessage id="result-success.success.step2-operator" defaultMessage="Zhou Maomao" />
      <a href="">
        <DingdingOutlined style={{ color: '#00A0E9', marginLeft: 8 }} />
        <FormattedMessage id="result-success.success.step2-extra" defaultMessage="Urge" />
      </a>
    </div>
  </div>
);

const content = (
  <>
    <Descriptions
      title={formatMessage({
        id: 'result-success.success.operate-title',
        defaultMessage: 'Project Name',
      })}
    >
      <Descriptions.Item
        label={
          <FormattedMessage id="result-success.success.operate-id" defaultMessage="Project ID：" />
        }
      >
        23421
      </Descriptions.Item>
      <Descriptions.Item
        label={
          <FormattedMessage id="result-success.success.principal" defaultMessage="Principal：" />
        }
      >
        <FormattedMessage id="result-success.success.step1-operator" defaultMessage="Qu Lili" />
      </Descriptions.Item>
      <Descriptions.Item
        label={
          <FormattedMessage
            id="result-success.success.operate-time"
            defaultMessage="Effective time："
          />
        }
      >
        2016-12-12 ~ 2017-12-12
      </Descriptions.Item>
    </Descriptions>
    <br />
    <Steps progressDot current={1}>
      <Step
        title={
          <span style={{ fontSize: 14 }}>
            <FormattedMessage
              id="result-success.success.step1-title"
              defaultMessage="Create project"
            />
          </span>
        }
        description={desc1}
      />
      <Step
        title={
          <span style={{ fontSize: 14 }}>
            <FormattedMessage
              id="result-success.success.step2-title"
              defaultMessage="Departmental preliminary review"
            />
          </span>
        }
        description={desc2}
      />
      <Step
        title={
          <span style={{ fontSize: 14 }}>
            <FormattedMessage
              id="result-success.success.step3-title"
              defaultMessage="Financial review"
            />
          </span>
        }
      />
      <Step
        title={
          <span style={{ fontSize: 14 }}>
            <FormattedMessage id="result-success.success.step4-title" defaultMessage="Finish" />
          </span>
        }
      />
    </Steps>
  </>
);

const extra = (
  <Fragment>
    <Button type="primary">
      <FormattedMessage id="result-success.success.btn-return" defaultMessage="Back to list" />
    </Button>
    <Button>
      <FormattedMessage id="result-success.success.btn-project" defaultMessage="View project" />
    </Button>
    <Button>
      <FormattedMessage id="result-success.success.btn-print" defaultMessage="Print" />
    </Button>
  </Fragment>
);

export default () => (
  <GridContent>
    <Card bordered={false}>
      <Result
        status="success"
        title={formatMessage({ id: 'result-success.success.title' })}
        subTitle={formatMessage({ id: 'result-success.success.description' })}
        extra={extra}
        style={{ marginBottom: 16 }}
      >
        {content}
      </Result>
      <ScrollFollow
        startFollowing={true}
        render={({ follow, onScroll }: { follow: boolean; onScroll: (x: any) => void }) => (
          <LazyLog
            url="https://streaming-endpoint-hvj543v47j2e.runkit.sh/"
            stream
            follow={follow}
            onScroll={onScroll}
          />
        )}
      />
    </Card>
  </GridContent>
);
