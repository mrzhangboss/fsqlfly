import React, { Component, Fragment } from 'react';
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
import { TransformInfo, Namespace } from './data';
import { Dispatch } from 'redux';
import { ReloadOutlined } from '@ant-design/icons';

// @ts-ignore
import styles from '@/pages/resources/style.less';

const { Search } = Input;
import { AnyAction } from 'redux';
import { findDOMNode } from 'react-dom';
import Result from '@/pages/form/step-form/components/Result';
import { UNIQUE_NAME_RULES } from '@/utils/UNIQUE_NAME_RULES';
import AceEditor from 'react-ace';
import 'brace/mode/yaml';
import 'brace/theme/solarized_dark';
import 'brace/theme/github';
import TextArea from 'antd/es/input/TextArea';

interface BasicListProps extends FormComponentProps {
  listBasicList: TransformInfo[];
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

  showRunModal = (item: TransformInfo) => {
    this.setState({
      visible: true,
      done: false,
      msg: '',
    });
    const { dispatch } = this.props;
    dispatch({
      type: 'formStepForm/runCurrentTransform',
      payload: item,
      callback: (res: { msg: string; success: boolean }) => {
        this.setState({
          msg: res.msg,
          done: true,
          success: res.success,
        });
      },
    });
  };

  showEditModal = (item: TransformInfo) => {
    const { dispatch } = this.props;
    dispatch({
      type: 'formStepForm/initStepFromList',
      payload: item,
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

  handleSubmit = () => {};

  deleteItem = (id: number) => {
    // @ts-ignore
    const { dispatch } = this.props;
    dispatch({
      type: 'transform/submit',
      payload: { id },
    });
  };
  getNamespace = (id: number) => {
    const { namespaces } = this.props;
    const data = namespaces.filter(x => x.id === id);
    return data.length > 0 ? data[0] : { name: 'DEFAULT', id: 0, avatar: '' };
  };

  render() {
    const { loading, namespaces } = this.props;

    const { search, current, edithDone, edithSubmit } = this.state;
    const { listBasicList } = this.props;

    const editAndDelete = (key: string, currentItem: TransformInfo) => {
      if (key === 'run') this.showRunModal(currentItem);
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
          <Tag>{this.getNamespace(namespaceId).name}</Tag>
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
            <Menu.Item key="run">运行</Menu.Item>
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
    const editModalFooter = edithDone
      ? { footer: null, onCancel: this.handleCancel }
      : {
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
            <Button type="primary" onClick={x => this.showRunModal(null)} loading={edithSubmit}>
              调试
            </Button>,
          ],
        };
    const {
      form: { getFieldDecorator },
    } = this.props;
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
                    avatar={
                      <Avatar
                        src={this.getNamespace(item.namespaceId).avatar}
                        shape="square"
                        size="large"
                      />
                    }
                    title={
                      <a href={this.getNamespace(item.namespaceId).avatar}>
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
            errorInfo={this.state.msg}
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

            <FormItem label="命名空间" {...this.formLayout}>
              {getFieldDecorator('namespaceId', {
                initialValue:
                  current === undefined || current.namespaceId === null ? 0 : current.namespaceId,
                rules: [
                  {
                    required: true,
                  },
                ],
              })(
                <Select placeholder="请选择" size="default" style={{ width: 120 }}>
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
                value={current?.sql}
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
                onChange={x => this.setState({ current: { ...current, config: x } })}
                name="functionConstructorConfig"
                editorProps={{ $blockScrolling: true }}
                readOnly={false}
                placeholder={'请输入Yaml配置'}
                defaultValue={current === undefined ? '' : current.config}
                value={current?.config}
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
                    initialValue: current?.isAvailable,
                    valuePropName: 'checked',
                  })(<Switch checkedChildren="启用" unCheckedChildren="禁止" />)}
                </Col>
                <Col span={3}>
                  {getFieldDecorator('isPublish', {
                    initialValue: current?.isPublish,
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
    transform: { list: TransformInfo[]; dependence: Namespace[] };
    loading: {
      models: { [key: string]: boolean };
    };
  }) => ({
    listBasicList: transform.list,
    namespaces: transform.dependence,
    loading: loading.models.namespace,
  }),
)(finalForm);
