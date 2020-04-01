import React, { Component } from 'react';
import { connect } from 'dva';
import { DownOutlined } from '@ant-design/icons';
import { Form } from '@ant-design/compatible';
import '@ant-design/compatible/assets/index.css';
import {
  List,
  Tooltip,
  Card,
  Button,
  Dropdown,
  Menu,
  Modal,
  Tag,
  message,
  Radio,
  Input,
  Avatar,
  Progress,
} from 'antd';
import { FormComponentProps } from '@ant-design/compatible/es/form';
import { JobInfo } from './data';
import { Namespace } from '@/pages/resources/data';
import { Dispatch } from 'redux';
import { ReloadOutlined } from '@ant-design/icons';
// @ts-ignore
import styles from '@/pages/resources/style.less';

import { AnyAction } from 'redux';

interface BasicListProps extends FormComponentProps {
  listBasicList: JobInfo[];
  namespaces: Namespace[];
  dispatch: Dispatch<AnyAction>;
  loading: boolean;
}

interface BasicListState {
  search: string;
  tag: number;
}

const NAMESPACE = 'job';

class BasicList extends Component<BasicListProps, BasicListState> {
  state: BasicListState = {
    search: '',
    tag: 0,
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

  stopRunTerminal = (item: JobInfo) => {
    const { dispatch } = this.props;
    dispatch({
      type: `${NAMESPACE}/run`,
      payload: {
        ...item,
        method: 'cancel',
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
          message.error(res.msg);
        }
      },
    });
  };

  getListContent = () => {
    const { tag, search } = this.state;
    const { listBasicList } = this.props;
    return listBasicList.filter(
      x => x.name.indexOf(search) >= 0 && (tag !== 0 ? x.namespaceId === tag : true),
    );
  };

  getNamespace = (id?: number) => {
    if (id === undefined) {
      return null;
    }
    const { namespaces } = this.props;
    const ns = namespaces.filter(x => x.id === id);
    if (ns.length === 0) return null;
    return ns[0];
  };
  getNamespaceAvatar = (item: JobInfo) => {
    const namespace = this.getNamespace(item.namespaceId);
    if (namespace === null) {
      return (
        <Avatar alt={item.info} shape="circle" size="large">
          {item.name.substr(0, 2)}
        </Avatar>
      );
    }
    return (
      <Avatar
        src={namespace === null ? '' : namespace.avatar}
        alt={item.info}
        shape="circle"
        size="large"
      />
    );
  };

  getNamespaceTitle = (id?: number) => {
    const namespace = this.getNamespace(id);
    if (namespace === null) {
      return <Tag>---</Tag>;
    }
    return <Tag>{namespace.name}</Tag>;
  };

  render() {
    const { namespaces, loading } = this.props;

    const confirmStopCurrentTerminal = (key: string, currentItem: JobInfo) => {
      if (key == 'stop') {
        Modal.confirm({
          title: '停止Flink任务',
          content: '确定停止Flink任务吗？',
          okText: '确认',
          cancelText: '取消',
          onOk: () => this.stopRunTerminal(currentItem),
        });
      } else {
        window.location.href = key;
      }
    };
    const RadioGroup = Radio.Group;
    const RadioButton = Radio.Button;
    const { Search } = Input;
    const { search } = this.state;

    const extraContent = (
      <div className={styles.extraContent}>
        <Button onClick={this.doRefresh} style={{ marginRight: 20 }}>
          <ReloadOutlined />
        </Button>
        <RadioGroup defaultValue={null} onChange={x => this.setState({ tag: x.target.value })}>
          <RadioButton value={0}>全部</RadioButton>
          {namespaces.length > 0 &&
            namespaces.map((x: Namespace) => {
              return (
                <RadioButton key={x.id} value={x.id}>
                  {x.name}
                </RadioButton>
              );
            })}
        </RadioGroup>
        <Search
          defaultValue={search}
          className={styles.extraContentSearch}
          placeholder="请输入名或者命名空间搜索"
          onSearch={value => this.setState({ search: value })}
        />
      </div>
    );
    const ListContent = ({
      data: { name, startTime, endTime, status, namespaceId, duration },
    }: {
      data: JobInfo;
    }) => (
      <div className={styles.listContent}>
        <div className={styles.listContentItem}>{this.getNamespaceTitle(namespaceId)}</div>

        <div className={styles.listContentItem}>
          <span>开始时间</span>
          <Tooltip placement="top" title={duration}>
            <p>{startTime}</p>
          </Tooltip>
        </div>
        <div className={styles.listContentItem}>
          <span>结束时间</span>
          <p>{endTime === '-' ? '0000-00-00 00:00:00' : endTime}</p>
        </div>

        <div className={styles.listContentItem}>
          <Progress
            type="circle"
            percent={100}
            status={status === 'RUNNING' ? 'success' : 'exception'}
            strokeWidth={1}
            width={50}
            style={{ width: 180 }}
          />
        </div>
      </div>
    );

    const MoreBtn: React.SFC<{
      item: JobInfo;
    }> = ({ item }) => (
      <Dropdown
        overlay={
          <Menu onClick={({ key }) => confirmStopCurrentTerminal(key, item)}>
            <Menu.Item key="stop">停止</Menu.Item>
            {item.url !== undefined && <Menu.Item key={item.url}>连接</Menu.Item>}
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
            title="Flink Job"
            style={{ marginTop: 24 }}
            bodyStyle={{ padding: '0 32px 40px 32px' }}
            extra={extraContent}
          >
            <List
              size="large"
              rowKey="id"
              loading={loading}
              dataSource={this.getListContent()}
              renderItem={item => (
                <List.Item
                  actions={[
                    <a href={item.detailUrl} target="_blank">
                      详情
                    </a>,
                    <MoreBtn key="more" item={item} />,
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <a href={item.detailUrl} target="_blank">
                        {item.name}
                      </a>
                    }
                    avatar={this.getNamespaceAvatar(item)}
                    description={item.info}
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
    job,
    loading,
  }: {
    job: { list: JobInfo[]; dependence: Namespace[] };
    loading: {
      models: { [key: string]: boolean };
    };
  }) => ({
    listBasicList: job.list,
    namespaces: job.dependence,
    loading: loading.models.namespace,
  }),
)(finalForm);
