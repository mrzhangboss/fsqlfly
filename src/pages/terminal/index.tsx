import React, { Component } from 'react';
import { connect } from 'dva';
import { DownOutlined } from '@ant-design/icons';
import { Form } from '@ant-design/compatible';
import '@ant-design/compatible/assets/index.css';
import { List, Card, Button, Dropdown, Menu, Modal, Tag, message } from 'antd';
import { FormComponentProps } from '@ant-design/compatible/es/form';
import { TerminalInfo } from './data';
import { Namespace, Resource } from '@/pages/resources/data';
import { Link } from 'umi';
import { Dispatch } from 'redux';
import { ReloadOutlined } from '@ant-design/icons';
// @ts-ignore
import styles from '@/pages/resources/style.less';

import { AnyAction } from 'redux';

interface BasicListProps extends FormComponentProps {
  listBasicList: TerminalInfo[];
  namespaces: Namespace[];
  dispatch: Dispatch<AnyAction>;
  loading: boolean;
}

interface BasicListState {
  visible: boolean;
  editVisible: boolean;
  edithDone: boolean;
  edithSubmit: boolean;
  done: boolean;
  current?: TerminalInfo;
  search: string;
  msg: string;
  success: boolean;
  submitted: boolean;
  searchResult: TerminalInfo[];
  tag: number;
}

const NAMESPACE = 'terminal';

class BasicList extends Component<BasicListProps, BasicListState> {
  state: BasicListState = {
    visible: false,
    done: false,
    current: undefined,
    search: '',
    msg: '',
    success: false,
    submitted: false,
    searchResult: [],
    tag: 0,
    editVisible: false,
    edithDone: false,
    edithSubmit: false,
  };

  componentDidMount() {
    // @ts-ignore
    this.doRefresh();
  }

  doRefresh = () => {
    const { dispatch } = this.props;
    dispatch({
      type: `${NAMESPACE}/fetch`,
    });
  };

  stopRunTerminal = (item: TerminalInfo) => {
    const { dispatch } = this.props;
    dispatch({
      type: `${NAMESPACE}/run`,
      payload: {
        ...item,
        method: 'stop',
        model: NAMESPACE,
      },
      callback: (res: { msg: string; success: boolean }) => {
        if (res.success) {
          message.success('删除成功！');
          dispatch({
            type: `${NAMESPACE}/deleteOne`,
            payload: { id: item.id },
          });
        } else {
          message.success('成功！');
        }
      },
    });
  };

  render() {
    const { loading } = this.props;

    const { listBasicList } = this.props;

    const confirmStopCurrentTerminal = (key: string, currentItem: TerminalInfo) => {
      Modal.confirm({
        title: '删除TERMINAL',
        content: '确定删除该TERMINAL吗？',
        okText: '确认',
        cancelText: '取消',
        onOk: () => this.stopRunTerminal(currentItem),
      });
    };

    const extraContent = (
      <div className={styles.extraContent}>
        <Button onClick={this.doRefresh} style={{ marginRight: 20 }}>
          <ReloadOutlined />
        </Button>
      </div>
    );
    const ListContent = ({ data: { name } }: { data: TerminalInfo }) => (
      <div className={styles.listContent}></div>
    );

    const MoreBtn: React.SFC<{
      item: TerminalInfo;
    }> = ({ item }) => (
      <Dropdown
        overlay={
          <Menu onClick={({ key }) => confirmStopCurrentTerminal(key, item)}>
            <Menu.Item key="stop">停止</Menu.Item>
          </Menu>
        }
      >
        <a>
          更多 <DownOutlined />
        </a>
      </Dropdown>
    );

    // @ts-ignore
    return (
      <>
        <div className={styles.standardList}>
          <Card
            className={styles.listCard}
            bordered={false}
            title="terminal"
            style={{ marginTop: 24 }}
            bodyStyle={{ padding: '0 32px 40px 32px' }}
            extra={extraContent}
          >
            <List
              size="large"
              rowKey="id"
              loading={loading}
              dataSource={listBasicList}
              renderItem={item => (
                <List.Item
                  actions={[
                    <Link to={`/terminal/${item.id}`}>连接</Link>,
                    <MoreBtn key="more" item={item} />,
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <a href={'#'}>
                        <Tag>{item.name}</Tag>
                      </a>
                    }
                  />
                  <ListContent data={item} />
                </List.Item>
              )}
            />
          </Card>
        </div>
      </>
    );
  }
}

const finalForm = Form.create<BasicListProps>()(BasicList);

export default connect(
  ({
    terminal,
    loading,
  }: {
    terminal: { list: TerminalInfo[]; dependence: Namespace[]; dependence1: Resource[] };
    loading: {
      models: { [key: string]: boolean };
    };
  }) => ({
    listBasicList: terminal.list,
    namespaces: terminal.dependence,
    loading: loading.models.namespace,
  }),
)(finalForm);
