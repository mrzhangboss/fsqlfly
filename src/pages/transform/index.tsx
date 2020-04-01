import React, { Component } from 'react';
import moment from 'moment';
import { connect } from 'dva';
import { DownOutlined, PlusOutlined } from '@ant-design/icons';
import { Form } from '@ant-design/compatible';
import '@ant-design/compatible/assets/index.css';
import {
  List,
  Card,
  Input,
  Progress,
  Button,
  Dropdown,
  Menu,
  Avatar,
  Modal,
  Tag,
  Radio,
  Select,
  Row,
  Col,
  Switch,
} from 'antd';
import { FormComponentProps } from '@ant-design/compatible/es/form';
import { TransformInfo } from './data';
import { Namespace, Resource } from '@/pages/resources/data';

import { Dispatch } from 'redux';
import { ReloadOutlined } from '@ant-design/icons';
import { CopyToClipboard } from 'react-copy-to-clipboard';
// @ts-ignore
import styles from '@/pages/resources/style.less';

const { Search } = Input;
const { Option } = Select;
import { AnyAction } from 'redux';
import { findDOMNode } from 'react-dom';
import Result from '@/pages/resources/components/Result';
import { UNIQUE_NAME_RULES } from '@/utils/UNIQUE_NAME_RULES';
import AceEditor from 'react-ace';
import 'brace/mode/yaml';
import 'brace/theme/solarized_dark';
import 'brace/theme/github';
import TextArea from 'antd/es/input/TextArea';

interface BasicListProps extends FormComponentProps {
  listBasicList: TransformInfo[];
  namespaces: Namespace[];
  resources: Resource[];
  dispatch: Dispatch<AnyAction>;
  loading: boolean;
}

interface BasicListState {
  visible: boolean;
  editVisible: boolean;
  edithDone: boolean;
  edithSubmit: boolean;
  done: boolean;
  current?: Partial<TransformInfo>;
  search: string;
  msg: string;
  success: boolean;
  submitted: boolean;
  searchResult: TransformInfo[];
  tag: number;
}

const NAMESPACE = 'transform';

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

  formLayout = {
    labelCol: { span: 5 },
    wrapperCol: { span: 17 },
  };

  addBtn: HTMLButtonElement | undefined | null;

  normFile = (e: Event & { fileList: Array<string> }) => {
    console.log('Upload event:', e);
    if (Array.isArray(e)) {
      return e;
    }
    return e && e.fileList;
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

  showModal = () => {
    this.setState({ editVisible: true, current: undefined });
  };

  showRunModal = (item: TransformInfo, method: string) => {
    this.setState({
      visible: true,
      done: false,
      msg: '',
    });
    const { dispatch } = this.props;
    dispatch({
      type: 'transform/run',
      payload: {
        ...item,
        method: method,
        model: 'transform',
      },
      callback: (res: { msg: string; success: boolean }) => {
        this.setState({
          msg: res.msg,
          done: true,
          success: res.success,
        });
      },
    });
  };

  showDebugResult = () => {
    this.setState({ edithSubmit: true });
    const { form, dispatch } = this.props;
    const { current } = this.state;
    form.validateFields((err: string | undefined, fieldsValue: any) => {
      if (err) {
        this.setState({ edithSubmit: false });
        return;
      }

      this.setState({ submitted: true });
      dispatch({
        type: 'transform/run',
        payload: {
          ...fieldsValue,
          ...current,
          method: 'debug',
          id: 0,
          model: 'transform',
        },
        callback: (res: { success: boolean; msg: string; data: { url: string } }) => {
          this.setState({
            edithSubmit: false,
          });
          if (res.success) {
            window.open(res.data.url);
          } else {
            this.setState({ msg: res.msg, success: false, done: true, visible: true });
          }
        },
      });
    });
  };

  showEditModal = (item: TransformInfo) => {
    this.setState({
      editVisible: true,
      current: item,
    });
  };

  handleDone = () => {
    setTimeout(() => this.addBtn && this.addBtn.blur(), 0);

    this.setState({
      done: false,
      visible: false,
    });
  };

  handleCancel = () => {
    setTimeout(() => this.addBtn && this.addBtn.blur(), 0);
    this.setState({
      editVisible: false,
    });
  };

  handleSubmit = () => {
    const { form, dispatch } = this.props;
    const { current } = this.state;
    this.setState({ visible: true, done: false, msg: '...' });
    form.validateFields((err: string | undefined, fieldsValue: Resource) => {
      if (err) return;
      this.setState({ submitted: true });
      dispatch({
        type: 'transform/submit',
        payload: { ...current, ...fieldsValue },
        callback: (res: { success: boolean; msg: string }) => {
          if (res.success) {
            this.setState({
              edithDone: false,
              editVisible: false,
              success: res.success,
              msg: res.msg,
              visible: false,
              edithSubmit: false,
            });
          } else {
            this.setState({
              done: true,
              visible: true,
              success: res.success,
              msg: res.msg,
              edithSubmit: false,
            });
          }
        },
      });
    });
  };
  handleChange = (selects: string[]) => {
    const { current } = this.state;
    const va = selects.join(',');
    const newV = current === undefined ? { require: va } : { ...current, require: va };
    this.setState({ current: newV });
  };

  deleteItem = (id: number) => {
    // @ts-ignore
    const { dispatch } = this.props;
    dispatch({
      type: 'transform/submit',
      payload: { id },
    });
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

  getNamespaceTitle = (id?: number) => {
    const namespace = this.getNamespace(id);
    return namespace === null ? '' : namespace.name;
  };

  getNamespaceAvatar = (item: TransformInfo) => {
    const namespace = this.getNamespace(item.namespaceId);
    if (namespace === null) {
      return (
        <Avatar alt={item.info} shape="square" size="large">
          {item.name.substr(0, 2)}
        </Avatar>
      );
    }
    return (
      <Avatar
        src={namespace === null ? '' : namespace.avatar}
        alt={item.info}
        shape="square"
        size="large"
      />
    );
  };

  render() {
    const { loading, namespaces } = this.props;

    const { search, current, edithSubmit } = this.state;
    const { listBasicList } = this.props;

    const editAndDelete = (key: string, currentItem: TransformInfo) => {
      if (key === 'start' || key === 'stop' || key === 'restart')
        this.showRunModal(currentItem, key);
      else if (key === 'delete') {
        Modal.confirm({
          title: '删除任务',
          content: '确定删除该任务吗？',
          okText: '确认',
          cancelText: '取消',
          onOk: () => this.deleteItem(currentItem.id !== undefined ? currentItem.id : 0),
        });
      }
    };
    const RadioGroup = Radio.Group;
    const RadioButton = Radio.Button;

    const extraContent = (
      <div className={styles.extraContent}>
        <Button onClick={this.doRefresh}>
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
          placeholder="请输入项目名或者命名空间搜索"
          onSearch={value => this.setState({ search: value })}
        />
      </div>
    );
    const ListContent = ({
      data: { name, info, isAvailable, isPublish, createAt, updateAt, namespaceId },
    }: {
      data: TransformInfo;
    }) => (
      <div className={styles.listContent}>
        <div className={styles.listContentItem}>
          <Tag>{this.getNamespaceTitle(namespaceId)}</Tag>
        </div>
        <div className={styles.listContentItem}>
          <span>创建时间</span>
          <p>{moment(createAt).format('YYYY-MM-DD HH:mm')}</p>
        </div>
        <div className={styles.listContentItem}>
          <span>修改时间</span>
          <p>{moment(updateAt).format('YYYY-MM-DD HH:mm')}</p>
        </div>
        <div className={styles.listContentItem}>
          <Progress
            type="circle"
            percent={100}
            status={isAvailable ? (isPublish ? 'success' : 'normal') : 'exception'}
            strokeWidth={1}
            width={50}
            style={{ width: 180 }}
          />
        </div>
      </div>
    );

    const MoreBtn: React.SFC<{
      item: TransformInfo;
    }> = ({ item }) => (
      <Dropdown
        overlay={
          <Menu onClick={({ key }) => editAndDelete(key, item)}>
            <Menu.Item key="delete">删除</Menu.Item>
            <Menu.Item key="start">运行</Menu.Item>
            <Menu.Item key="stop">停止</Menu.Item>
            <Menu.Item key="restart">重启</Menu.Item>
            <Menu.Item key="copy">
              <CopyToClipboard
                text={item.require}
                onCopy={() => this.setState({ edithDone: true })}
              >
                <span>复制依赖</span>
              </CopyToClipboard>
            </Menu.Item>
          </Menu>
        }
      >
        <a>
          更多 <DownOutlined />
        </a>
      </Dropdown>
    );
    const FormItem = Form.Item;
    const SelectOption = Select.Option;
    const editModalFooter = {
      okText: '保存',
      onOk: this.handleSubmit,
      onCancel: this.handleCancel,
      footer: [
        <Button key="back" onClick={this.handleCancel}>
          取消
        </Button>,
        <Button key="submit" type="primary" loading={edithSubmit} onClick={this.handleSubmit}>
          保存
        </Button>,
        <Button type="primary" onClick={x => this.showDebugResult()} loading={edithSubmit}>
          调试
        </Button>,
      ],
    };
    const {
      form: { getFieldDecorator },
      resources,
    } = this.props;

    const getRealNamespaceName = (id: number, tab: string) => {
      let names = namespaces.filter(x => x.id === id);
      return names.length === 0 ? tab : names[0].name + '.' + tab;
    };
    const getName = (x: Resource) =>
      x.namespaceId !== undefined && x.namespaceId !== null
        ? getRealNamespaceName(x.namespaceId, x.name)
        : x.name;

    const resourceSelect = Array.isArray(resources)
      ? resources.map(x => (
          <Option key={x.id} title={x.info} value={getName(x)}>
            {getName(x)}
          </Option>
        ))
      : [];

    // @ts-ignore
    return (
      <>
        <div className={styles.standardList}>
          <Card
            className={styles.listCard}
            bordered={false}
            title="资源"
            style={{ marginTop: 24 }}
            bodyStyle={{ padding: '0 32px 40px 32px' }}
            extra={extraContent}
          >
            <Button
              type="dashed"
              style={{ width: '100%', marginBottom: 8 }}
              icon={<PlusOutlined />}
              onClick={this.showModal}
              ref={component => {
                this.addBtn = findDOMNode(component) as HTMLButtonElement;
              }}
            >
              添加
            </Button>

            <List
              size="large"
              rowKey="id"
              loading={loading}
              dataSource={listBasicList.filter(
                x =>
                  x.name.indexOf(search) >= 0 &&
                  (this.state.tag !== 0 ? x.namespaceId === this.state.tag : true),
              )}
              renderItem={item => (
                <List.Item
                  actions={[
                    <a
                      key="edit"
                      onClick={e => {
                        e.preventDefault();
                        this.showEditModal(item);
                      }}
                    >
                      编辑
                    </a>,
                    <MoreBtn key="more" item={item} />,
                  ]}
                >
                  <List.Item.Meta
                    avatar={this.getNamespaceAvatar(item)}
                    title={
                      <a href="#">
                        {item.name.length < 8 ? item.name : item.name.substring(0, 8) + '...'}
                      </a>
                    }
                    description={item.info.length < 10 ? item.info : item.info.substring(0, 10)}
                  />
                  <ListContent data={item} />
                </List.Item>
              )}
            />
          </Card>
        </div>
        <Modal
          title={`运行结果`}
          className={styles.standardListForm}
          width={1080}
          bodyStyle={{ padding: '72px 0' }}
          destroyOnClose
          visible={this.state.visible}
          onCancel={x => this.setState({ visible: false })}
          footer={null}
          confirmLoading={this.state.done}
        >
          <Result
            type={this.state.done ? (this.state.success ? 'success' : 'error') : 'line'}
            title={this.state.done ? (this.state.success ? '运行成功' : '运行失败') : `提交中...`}
            description={this.state.msg}
            actions={
              <Button
                loading={!this.state.done}
                type="primary"
                onClick={x => this.setState({ visible: false })}
              >
                知道了
              </Button>
            }
            className={styles.formResult}
          />
        </Modal>

        <Modal
          title={current === undefined ? null : current.id === undefined ? '新增' : '编辑'}
          className={styles.standardListForm}
          width={1080}
          bodyStyle={{ padding: '72px 0' }}
          destroyOnClose
          visible={this.state.editVisible}
          {...editModalFooter}
        >
          <Form onSubmit={this.handleSubmit}>
            <FormItem label="名称" {...this.formLayout}>
              {getFieldDecorator('name', {
                rules: UNIQUE_NAME_RULES,
                initialValue: current === undefined ? '' : current.name,
              })(<Input placeholder="请输入" />)}
            </FormItem>
            <FormItem label="介绍" {...this.formLayout}>
              {getFieldDecorator('info', {
                initialValue: current === undefined ? '' : current.info,
              })(<TextArea placeholder="请输入" />)}
            </FormItem>
            <FormItem label="依赖" {...this.formLayout}>
              <Select
                mode="tags"
                style={{ width: '100%' }}
                onChange={this.handleChange}
                tokenSeparators={[',']}
                defaultValue={
                  current === undefined || current.require === undefined
                    ? undefined
                    : current.require.split(',')
                }
              >
                {resourceSelect}
              </Select>
            </FormItem>

            <FormItem label="命名空间" {...this.formLayout}>
              {getFieldDecorator('namespaceId', {
                initialValue:
                  current === undefined || current.namespaceId === null ? 0 : current.namespaceId,
                rules: [
                  {
                    required: false,
                  },
                ],
              })(
                <Select placeholder="请选择" size="large" style={{ width: 120 }}>
                  <SelectOption key={-1} value={0}>
                    默认
                  </SelectOption>
                  {namespaces.length > 0 &&
                    namespaces.map(x => {
                      return (
                        <SelectOption key={x.id} value={x.id}>
                          {x.name}
                        </SelectOption>
                      );
                    })}
                </Select>,
              )}
            </FormItem>
            <FormItem label="SQL" {...this.formLayout}>
              <AceEditor
                mode="sql"
                theme="github"
                onChange={x => this.setState({ current: { ...current, sql: x } })}
                name="functionConstructorConfig"
                editorProps={{ $blockScrolling: true }}
                readOnly={false}
                placeholder={'请输入Yaml配置'}
                defaultValue={current === undefined ? '' : current.sql}
                value={current === undefined ? '' : current.sql}
                //@ts-ignore
                width={765}
                //@ts-ignore
                height={650}
              />
            </FormItem>
            <FormItem label="配置文件" {...this.formLayout}>
              <AceEditor
                mode="yaml"
                theme="solarized_dark"
                onChange={x => this.setState({ current: { ...current, yaml: x } })}
                name="functionConstructorConfig"
                editorProps={{ $blockScrolling: true }}
                readOnly={false}
                placeholder={'请输入Yaml配置'}
                defaultValue={current === undefined ? '' : current.yaml}
                value={current === undefined ? '' : current.yaml}
                //@ts-ignore
                width={765}
                //@ts-ignore
                height={650}
              />
            </FormItem>
            <FormItem label="其他" {...this.formLayout}>
              <Row gutter={16}>
                <Col span={3}>
                  {getFieldDecorator('isAvailable', {
                    initialValue: current === undefined ? false : current.isAvailable,
                    valuePropName: 'checked',
                  })(<Switch checkedChildren="启用" unCheckedChildren="禁止" />)}
                </Col>
                <Col span={3}>
                  {getFieldDecorator('isPublish', {
                    initialValue: current === undefined ? false : current.isPublish,
                    valuePropName: 'checked',
                  })(<Switch checkedChildren="发布" unCheckedChildren="开发" />)}
                </Col>
              </Row>
            </FormItem>
          </Form>
        </Modal>
      </>
    );
  }
}

const finalForm = Form.create<BasicListProps>()(BasicList);

export default connect(
  ({
    transform,
    loading,
  }: {
    transform: { list: TransformInfo[]; dependence: Namespace[]; dependence1: Resource[] };
    loading: {
      models: { [key: string]: boolean };
    };
  }) => ({
    listBasicList: transform.list,
    namespaces: transform.dependence,
    loading: loading.models.namespace,
    resources: transform.dependence1,
  }),
)(finalForm);
