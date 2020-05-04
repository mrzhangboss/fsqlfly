import React, { Component } from 'react';
import { findDOMNode } from 'react-dom';
import moment from 'moment';
import { connect } from 'dva';
import { DownOutlined, PlusOutlined, ReloadOutlined } from '@ant-design/icons';
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
  Modal,
  Row,
  Col,
  Switch,
  Select,
  Tag,
  Radio,
  Tooltip,
} from 'antd';
import { FormComponentProps } from '@ant-design/compatible/es/form';
import { Connection } from '../data';
import { Dispatch } from 'redux';
import Result from '../components/Result';
import { PageHeaderWrapper } from '@ant-design/pro-layout';
import { cutStr, CONNECTION_TEMPLATE, getStatus } from '@/utils/utils';
import AceEditor from 'react-ace';
import 'brace/mode/yaml';
import 'brace/mode/ini';

const SelectOption = Select.Option;
const FormItem = Form.Item;
const { Search } = Input;
import { AnyAction } from 'redux';
import { UNIQUE_NAME_RULES } from '@/utils/UNIQUE_NAME_RULES';
// @ts-ignore
import styles from '../style.less';
import { RadioChangeEvent } from 'antd/lib/radio/interface';
import { UserModelState } from '@/models/user';
import { Link } from 'umi';

interface BasicListProps extends FormComponentProps {
  listBasicList: Connection[];
  dispatch: Dispatch<AnyAction>;
  total: number;
  loading: boolean;
  fetchLoading: boolean;
  deletable: boolean;
}

interface BasicListState {
  visible: boolean;
  runVisible: boolean;
  runDone: boolean;
  done: boolean;
  current?: Partial<Connection>;
  search: string;
  tag: string;
  connector: string;
  config?: string;
  type: string;
  msg: string;
  success: boolean;
  submitted: boolean;
  pageSize: number;
  currentPage: number;
}

const RadioGroup = Radio.Group;
const RadioButton = Radio.Button;
const NAMESPACE = 'connection';

@connect(
  ({
    connection,
    loading,
    total,
    user,
  }: {
    connection: { list: Connection[] };
    loading: {
      models: { [key: string]: boolean };
      effects: { [key: string]: boolean };
    };
    total: number;
    user: UserModelState;
  }) => ({
    listBasicList: connection.list,
    loading: loading.models.connection,
    fetchLoading: loading.effects['connection/fetch'],
    deletable: user.currentUser?.deletable,
  }),
)
class BasicList extends Component<BasicListProps, BasicListState> {
  state: BasicListState = {
    visible: false,
    runVisible: false,
    runDone: false,
    done: false,
    current: undefined,
    search: '',
    msg: '',
    success: false,
    submitted: false,
    pageSize: 5,
    currentPage: 1,
    tag: '',
    connector: '',
    type: '',
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
    this.setState({
      visible: true,
      submitted: false,
      current: {},
      connector: '',
    });
  };

  showEditModal = (item: Connection) => {
    this.setState({
      visible: true,
      current: item,
      submitted: false,
      connector: item.connector,
      config: item.config,
    });
  };

  showManageModal = (item: Connection, mode: string) => {
    this.setState({
      runVisible: true,
      runDone: false,
      msg: '',
    });
    const { dispatch } = this.props;
    dispatch({
      type: `${NAMESPACE}/run`,
      payload: { method: mode, model: NAMESPACE, id: item.id },
      callback: (res: { msg: string; success: boolean }) => {
        this.setState({
          msg: res.msg,
          runDone: true,
          success: res.success,
        });
      },
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
      visible: false,
    });
  };

  handleUpdate = (e: React.FormEvent) => {
    this.handleSubmit(e, true);
  };

  handleSubmit = (e: React.FormEvent, isUpdate?: boolean) => {
    e.preventDefault();
    // @ts-ignore
    const { dispatch, form } = this.props;
    const { current } = this.state;

    setTimeout(() => this.addBtn && this.addBtn.blur(), 0);
    form.validateFields((err: string | undefined, fieldsValue: Connection) => {
      if (err) return;
      this.setState({ submitted: true });

      dispatch({
        type: `${NAMESPACE}/submit`,
        payload: { ...current, ...fieldsValue },
        callback: (res: { success: boolean; msg: string }) => {
          if (res.success) {
            this.setState({
              done: true,
              success: res.success,
              msg: res.msg,
            });
          } else {
            this.setState({
              runDone: true,
              success: res.success,
              msg: res.msg,
              submitted: false,
              runVisible: true,
            });
          }
        },
      });
    });
  };

  deleteItem = (id: number) => {
    // @ts-ignore
    const { dispatch } = this.props;
    dispatch({
      type: `${NAMESPACE}/submit`,
      payload: { id },
    });
  };

  onSearch = (value: string, event?: any) => {
    this.setState({ search: value, currentPage: 1 });
  };

  getFilterPageData = () => {
    const { search, tag } = this.state;
    const { listBasicList } = this.props;
    const res = listBasicList.filter(
      x =>
        (search.length === 0 || x.name.indexOf(search) >= 0) &&
        (tag.length === 0 || tag === x.type),
    );
    console.log(res.length);
    console.log(res);
    return res;
  };

  getCurrentPageData = () => {
    const { pageSize, currentPage } = this.state;
    const data = this.getFilterPageData();
    return data.slice((currentPage - 1) * pageSize, currentPage * pageSize);
  };

  onPageChange = (current: number, newPageSize: any) => {
    this.setState({ pageSize: newPageSize, currentPage: current });
  };

  onTagChage = (event: RadioChangeEvent) => {
    event.preventDefault();
    this.setState({ tag: event.target.value });
  };

  onSelectTypeChange = (value: any) => {
    console.log('value is ');
    console.log(value);
    const template = CONNECTION_TEMPLATE[value];
    if (template !== undefined)
      this.setState({
        connector: template,
        current: { ...this.state.current, connector: template },
      });
  };

  render() {
    const supportConnectionType = [
      'hive',
      'db',
      'kafka',
      'hbase',
      'elasticsearch',
      'canal',
      'file',
    ];
    const { loading } = this.props;
    const {
      form: { getFieldDecorator },
      fetchLoading,
    } = this.props;

    const {
      visible,
      done,
      current = {},
      search,
      success,
      msg,
      submitted,
      currentPage,
    } = this.state;

    const editAndDelete = (key: string, currentItem: Connection) => {
      if (key === 'edit') this.showEditModal(currentItem);
      else if (key == 'update') this.showManageModal(currentItem, 'update');
      else if (key == 'upgrade') this.showManageModal(currentItem, 'upgrade');
      else if (key === 'delete') {
        Modal.confirm({
          title: '删除',
          content: '确定删除吗？',
          okText: '确认',
          cancelText: '取消',
          onOk: () => this.deleteItem(currentItem.id),
        });
      }
    };
    const modalFooter = done
      ? { footer: null, onCancel: this.handleDone }
      : {
          okText: '保存',
          onOk: this.handleSubmit,
          onCancel: this.handleCancel,
          footer: [
            <Button key="back" onClick={this.handleCancel}>
              取消
            </Button>,
            <Button key="submit" type="primary" loading={submitted} onClick={this.handleSubmit}>
              保存
            </Button>,
          ],
        };

    const extraContent = (
      <div className={styles.extraContent}>
        <Button onClick={this.doRefresh} disabled={fetchLoading}>
          <ReloadOutlined />
        </Button>
        <RadioGroup defaultValue={null} onChange={this.onTagChage}>
          <RadioButton value={''}>全部</RadioButton>
          {supportConnectionType.map(x => {
            return (
              <RadioButton key={x} value={x}>
                {x}
              </RadioButton>
            );
          })}
        </RadioGroup>
        <Search
          defaultValue={search}
          className={styles.extraContentSearch}
          placeholder="请输入"
          onSearch={this.onSearch}
        />
      </div>
    );
    const ListContent = ({
      data: { name, type, isActive, isLocked, createAt, updateAt },
    }: {
      data: Connection;
    }) => (
      <div className={styles.listContent}>
        <div className={styles.listContentItem}>
          <p>
            <Tag>{type}</Tag>
          </p>
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
            status={getStatus(isActive, isLocked)}
            strokeWidth={1}
            width={50}
            style={{ width: 180 }}
          />
        </div>
      </div>
    );

    const { deletable } = this.props;
    const MoreBtn: React.SFC<{
      item: Connection;
    }> = ({ item }) => (
      <Dropdown
        overlay={
          <Menu onClick={({ key }) => editAndDelete(key, item)}>
            {deletable && <Menu.Item key="delete">删除</Menu.Item>}
            <Menu.Item key="update">更新</Menu.Item>
          </Menu>
        }
      >
        <a>
          更多 <DownOutlined />
        </a>
      </Dropdown>
    );
    const getModalContent = (isCreate: boolean) => {
      if (done) {
        return (
          <Result
            type={success ? 'success' : 'error'}
            title={`操作 ${success ? '成功' : '失败'}`}
            description={success ? '' : msg}
            actions={
              <Button type="primary" onClick={this.handleDone}>
                知道了
              </Button>
            }
            className={styles.formResult}
          />
        );
      }
      // @ts-ignore
      return (
        <Form onSubmit={this.handleSubmit}>
          <FormItem label="名称" {...this.formLayout}>
            {getFieldDecorator('name', {
              rules: isCreate ? UNIQUE_NAME_RULES : [],
              initialValue: current.name,
            })(<Input disabled={!isCreate} placeholder="请输入" />)}
          </FormItem>

          <FormItem label="介绍" {...this.formLayout}>
            {getFieldDecorator('info', {
              initialValue: current.info,
              rules: [
                {
                  required: false,
                },
              ],
            })(<Input.TextArea placeholder="简介" />)}
          </FormItem>

          <FormItem label="类型" {...this.formLayout}>
            {getFieldDecorator('type', {
              initialValue: current.type,
              rules: [
                {
                  required: true,
                },
              ],
            })(
              <Select
                disabled={!isCreate}
                size="middle"
                style={{ width: 140 }}
                onChange={this.onSelectTypeChange}
              >
                {supportConnectionType.map((x: string) => {
                  return (
                    <SelectOption key={x} value={x}>
                      {x}
                    </SelectOption>
                  );
                })}
              </Select>,
            )}
          </FormItem>

          <FormItem label="url" {...this.formLayout}>
            {getFieldDecorator('url', {
              initialValue: current.url,
              rules: [
                {
                  required: true,
                },
              ],
            })(<Input placeholder="数据库连接url" />)}
          </FormItem>

          <FormItem label="资源过滤正则" {...this.formLayout}>
            {getFieldDecorator('include', {
              initialValue: current.include,
              rules: [
                {
                  required: false,
                },
              ],
            })(<Input placeholder="使用逗号分割多个正则表达" />)}
          </FormItem>

          <FormItem label="资源排除" {...this.formLayout}>
            {getFieldDecorator('exclude', {
              initialValue: current.exclude,
              rules: [
                {
                  required: false,
                },
              ],
            })(<Input placeholder="使用逗号分割多个正则表达" />)}
          </FormItem>

          <FormItem label="connector" {...this.formLayout}>
            <AceEditor
              mode="yaml"
              onChange={x => this.setState({ connector: x, current: { ...current, connector: x } })}
              name="functionConstructorConfig"
              editorProps={{ $blockScrolling: true }}
              readOnly={false}
              placeholder={'请输入Yaml配置'}
              defaultValue={current.connector}
              value={this.state.connector}
              //@ts-ignore
              width={765}
              //@ts-ignore
              height={230}
            />
          </FormItem>

          <FormItem label="config" {...this.formLayout}>
            <AceEditor
              mode="ini"
              onChange={x => this.setState({ config: x, current: { ...current, config: x } })}
              name="functionConstructorConfig"
              editorProps={{ $blockScrolling: true }}
              readOnly={false}
              placeholder={'请输入Yaml配置'}
              defaultValue={current.config}
              value={this.state.config}
              //@ts-ignore
              width={765}
              //@ts-ignore
              height={230}
            />
          </FormItem>

          <FormItem label="自动更新周期（s）" {...this.formLayout}>
            {getFieldDecorator('updateInterval', {
              initialValue: current.updateInterval,
              rules: [
                {
                  required: false,
                },
              ],
            })(<Input type="number" placeholder="秒" width={20} />)}
          </FormItem>

          <FormItem label="其他" {...this.formLayout}>
            <Row gutter={16}>
              <Col span={3}>
                {getFieldDecorator('isActive', {
                  initialValue: current.isActive,
                  valuePropName: 'checked',
                })(<Switch checkedChildren="启用" unCheckedChildren="禁止" />)}
              </Col>
              <Col span={3}>
                {getFieldDecorator('isLocked', {
                  initialValue: current.isLocked,
                  valuePropName: 'checked',
                })(<Switch checkedChildren="锁" unCheckedChildren="开" />)}
              </Col>
            </Row>
          </FormItem>
        </Form>
      );
    };
    return (
      <>
        <PageHeaderWrapper>
          <div className={styles.standardList}>
            <Card
              className={styles.listCard}
              bordered={false}
              title="列表"
              style={{ marginTop: 24 }}
              bodyStyle={{ padding: '0 32px 40px 32px' }}
              extra={extraContent}
            >
              {currentPage === 1 && (
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
              )}
              <List
                size="large"
                rowKey="id"
                loading={loading}
                dataSource={this.getFilterPageData()}
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
                      <Link to={`/resources/connection/name/${item.id}`}>资源</Link>,
                      <MoreBtn key="more" item={item} />,
                    ]}
                  >
                    <List.Item.Meta
                      title={
                        <Tooltip title={item.name} placement="left">
                          <a href="#">{cutStr(item.name)}</a>
                        </Tooltip>
                      }
                      description={
                        <Tooltip title={item.info} placement="left">
                          <a href="#">{cutStr(item.info)}</a>
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
            visible={this.state.runVisible}
            onCancel={x => this.setState({ runVisible: false })}
            footer={null}
            confirmLoading={this.state.done}
          >
            <Result
              type={this.state.runDone ? (this.state.success ? 'success' : 'error') : 'line'}
              title={
                this.state.runDone ? (this.state.success ? '运行成功' : '运行失败') : `提交中...`
              }
              description={this.state.msg}
              actions={
                <Button
                  loading={!this.state.runDone}
                  type="primary"
                  onClick={x => this.setState({ runVisible: false })}
                >
                  知道了
                </Button>
              }
              className={styles.formResult}
            />
          </Modal>
        </PageHeaderWrapper>

        <Modal
          title={done ? null : `${current.id !== undefined ? '编辑' : '新增'}`}
          className={styles.standardListForm}
          width={1080}
          bodyStyle={done ? { padding: '72px 0' } : { padding: '28px 0 0' }}
          destroyOnClose
          visible={visible}
          {...modalFooter}
        >
          {getModalContent(current.id === undefined)}
        </Modal>
      </>
    );
  }
}

export default Form.create<BasicListProps>()(BasicList);
