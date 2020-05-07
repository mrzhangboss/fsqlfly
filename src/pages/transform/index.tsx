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
  Tooltip,
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
import { cutStr } from '@/utils/utils';

interface BasicListProps extends FormComponentProps {
  listBasicList: TransformInfo[];
  namespaces: Namespace[];
  resources: string[];
  dispatch: Dispatch<AnyAction>;
  loading: boolean;
}

interface BasicListState {
  visible: boolean;
  editVisible: boolean;
  edithDone: boolean;
  edithSubmit: boolean;
  done: boolean;
  current: Partial<TransformInfo>;
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
    current: {},
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
    this.setState({ editVisible: true, current: {} });
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
      submitted: false,
      edithSubmit: false,
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

  getNameTag = (id?: number) => {
    const name = this.getNamespaceTitle(id);
    return (
      <Tooltip title={name}>
        <div>
          <Tag>{cutStr(name)}</Tag>
        </div>
      </Tooltip>
    );
  };

  setTagValue = (v: number) => {
    this.setState({ tag: v });
  };

  getNamespaceAvatar = (item: TransformInfo) => {
    const namespace = this.getNamespace(item.namespaceId);
    if (namespace === null) {
      return (
        <Avatar alt={item.info} shape="square" size="large">
          DEFAULT
        </Avatar>
      );
    }
    return (
      <Avatar src={namespace.avatar} alt={item.info} shape="square" size="large">
        {namespace.avatar === undefined || namespace.avatar === null ? namespace.name : ''}
      </Avatar>
    );
  };

  render() {
    const { loading, namespaces } = this.props;

    const { search, current = {}, edithSubmit } = this.state;
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
        <RadioGroup defaultValue={null} onChange={x => this.setTagValue(x.target.value)}>
          <RadioButton className={styles.namespaceButton} value={0}>
            全部
          </RadioButton>
          {namespaces.length > 0 &&
            namespaces.slice(0, 8).map((x: Namespace) => {
              return (
                <Tooltip title={x.name} placement="left">
                  <RadioButton className={styles.namespaceButton} key={x.id} value={x.id}>
                    {cutStr(x.name)}
                  </RadioButton>
                </Tooltip>
              );
            })}
          {namespaces.length > 8 && (
            <Dropdown
              className={styles.namespaceButton}
              overlay={
                // @ts-ignore
                <Menu onClick={({ key }) => this.setTagValue(parseInt(key))}>
                  {namespaces.slice(8, namespaces.length + 1).map((x: Namespace) => {
                    return (
                      <Menu.Item key={x.id}>
                        <Tooltip title={x.name} placement="left">
                          <span>{cutStr(x.name)}</span>
                        </Tooltip>
                      </Menu.Item>
                    );
                  })}
                </Menu>
              }
            >
              <Button>
                更多
                <DownOutlined />
              </Button>
            </Dropdown>
          )}
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
      data: { name, info, isDaemon, createAt, updateAt, namespaceId },
    }: {
      data: TransformInfo;
    }) => (
      <div className={styles.listContent}>
        <div className={styles.listContentItem}>{this.getNameTag(namespaceId)}</div>
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
            status={isDaemon ? 'success' : 'normal'}
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

    const resourceSelect = Array.isArray(resources)
      ? resources.map(x => (
          <Option key={x} title={x} value={x}>
            {x}
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
                      <Tooltip title={item.name}>
                        <a href="#">{cutStr(item.name)}</a>
                      </Tooltip>
                    }
                    description={
                      <Tooltip title={item.info} placement="right">
                        <span>{cutStr(item.info)}</span>
                      </Tooltip>
                    }
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
                // @ts-ignore
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
                <Select>
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
                defaultValue={current.sql === undefined || current.sql === null ? '' : current.sql}
                value={current.sql === undefined || current.sql === null ? '' : current.sql}
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
                defaultValue={current.yaml === null ? '' : current.yaml}
                value={current.yaml === undefined || current.yaml === null ? '' : current.yaml}
                //@ts-ignore
                width={765}
                //@ts-ignore
                height={650}
              />
            </FormItem>
            <FormItem label="其他" {...this.formLayout}>
              <Row gutter={16}>
                <Col span={3}>
                  {getFieldDecorator('isDaemon', {
                    initialValue: current === undefined ? false : current.isDaemon,
                    valuePropName: 'checked',
                  })(<Switch checkedChildren="守护" unCheckedChildren="禁止" />)}
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
