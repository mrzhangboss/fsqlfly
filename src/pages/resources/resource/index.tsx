import React, { Component } from 'react';
import { findDOMNode } from 'react-dom';
import moment from 'moment';
import { connect } from 'dva';
import {
  List,
  Card,
  Input,
  Progress,
  Button,
  Icon,
  Dropdown,
  Menu,
  Modal,
  Form,
  Row,
  Col,
  Switch,
  Select,
  Avatar,
  Radio,
  Tag,
} from 'antd';
import { FormComponentProps } from 'antd/es/form';
import { Resource, Namespace } from '../data';
import { Dispatch } from 'redux';
import Result from '../components/Result';
import { PageHeaderWrapper } from '@ant-design/pro-layout';
import AceEditor from 'react-ace';
import 'brace/mode/yaml';
// import 'brace/theme/github';
// import 'brace/theme/chrome';
import 'brace/theme/solarized_dark';
import styles from '../style.less';

const SelectOption = Select.Option;
const RadioGroup = Radio.Group;
const RadioButton = Radio.Button;

const FormItem = Form.Item;
const { Search, TextArea } = Input;
import { AnyAction } from 'redux';
import { UploadFile } from 'antd/es/upload/interface';
import { RadioChangeEvent } from 'antd/lib/radio/interface';
import { UNIQUE_NAME_RULES } from '@/utils/UNIQUE_NAME_RULES';
const NAMESPACE = 'resource';
interface BasicListProps extends FormComponentProps {
  listBasicList: Resource[];
  dispatch: Dispatch<AnyAction>;
  loading: boolean;
  namespaces: Namespace[];
}

interface BasicListState {
  visible: boolean;
  done: boolean;
  current?: Partial<Resource>;
  search: string;
  msg: string;
  success: boolean;
  submitted: boolean;
  fileList: UploadFile[];
  pageSize: number;
  currentPage: number;
  tag: number;
  yaml: string;
}

@connect(
  ({
    loading,
    resource,
  }: {
    resource: { list: Resource[]; dependence: Namespace[] };
    loading: {
      models: { [key: string]: boolean };
    };
  }) => ({
    listBasicList: resource.list,
    loading: loading.models.file,
    namespaces: resource.dependence,
  }),
)
class BasicList extends Component<BasicListProps, BasicListState> {
  state: BasicListState = {
    visible: false,
    done: false,
    current: undefined,
    search: '',
    fileList: [],
    msg: '',
    success: false,
    submitted: false,
    pageSize: 5,
    currentPage: 1,
    tag: 0,
    yaml: '',
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
      fileList: [],
    });
  };

  showEditModal = (item: Resource) => {
    this.setState({
      visible: true,
      current: item,
      submitted: false,
      yaml: item.yaml,
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
    const { current, yaml } = this.state;

    setTimeout(() => this.addBtn && this.addBtn.blur(), 0);
    form.validateFields((err: string | undefined, fieldsValue: Resource) => {
      if (err) return;
      this.setState({ submitted: true });
      dispatch({
        type: 'resource/submit',
        payload: { ...current, ...fieldsValue, yaml },
        callback: (res: { success: boolean; msg: string }) => {
          this.setState({
            done: true,
            success: res.success,
            msg: res.msg,
          });
        },
      });
    });
  };

  deleteItem = (id: number) => {
    // @ts-ignore
    const { dispatch } = this.props;
    dispatch({
      type: 'resource/submit',
      payload: { id },
    });
  };

  onSearch = (value: string, event?: any) => {
    this.setState({ search: value, currentPage: 1 });
  };

  getAllData = () => {
    const { search, tag } = this.state;
    const { listBasicList } = this.props;
    return listBasicList.filter(
      x => x.name.indexOf(search) >= 0 && (tag !== 0 ? x.namespaceId === tag : true),
    );
  };

  getCurrentData = () => {
    const { pageSize, currentPage } = this.state;
    this.getAllData().slice((currentPage - 1) * pageSize, currentPage * pageSize);
  };

  getAvar = (id: number) => {
    const { namespaces } = this.props;
    const data = namespaces.filter(x => x.id === id);
    return data.length > 0 ? data[0].avatar : '';
  };

  onTagChage = (event: RadioChangeEvent) => {
    event.preventDefault();
    this.setState({ currentPage: 1, tag: event.target.value });
  };

  onPageChange = (current: number, newPageSize: any) => {
    this.setState({ pageSize: newPageSize, currentPage: current });
  };

  render() {
    const { loading, namespaces } = this.props;
    const {
      form: { getFieldDecorator },
    } = this.props;

    const {
      visible,
      done,
      current = {},
      search,
      success,
      msg,
      submitted,
      pageSize,
      currentPage,
    } = this.state;

    const editAndDelete = (key: string, currentItem: Resource) => {
      if (key === 'edit') this.showEditModal(currentItem);
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
        <Button onClick={this.doRefresh}>
          <Icon type="reload" />
        </Button>

        <RadioGroup defaultValue={null} onChange={this.onTagChage}>
          <RadioButton value={0}>全部</RadioButton>
          {namespaces.length > 0 &&
            namespaces.map(x => {
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
          placeholder="请输入"
          onSearch={this.onSearch}
        />
      </div>
    );
    const ListContent = ({
      data: { name, info, typ, isAvailable, isPublish, createAt, updateAt },
    }: {
      data: Resource;
    }) => (
      <div className={styles.listContent}>
        <div className={styles.listContentItem}>
          <Tag>{typ}</Tag>
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
      item: Resource;
    }> = ({ item }) => (
      <Dropdown
        overlay={
          <Menu onClick={({ key }) => editAndDelete(key, item)}>
            <Menu.Item key="delete">删除</Menu.Item>
          </Menu>
        }
      >
        <a>
          更多 <Icon type="down" />
        </a>
      </Dropdown>
    );
    const paginationProps = {
      showSizeChanger: true,
      showQuickJumper: true,
      onChange: this.onPageChange,
      onShowSizeChange: this.onPageChange,
    };
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
              rules: UNIQUE_NAME_RULES,
              initialValue: current.name,
            })(<Input placeholder="请输入" />)}
          </FormItem>
          <FormItem label="介绍" {...this.formLayout}>
            {getFieldDecorator('info', {
              initialValue: current.info,
            })(<TextArea placeholder="请输入" />)}
          </FormItem>

          <FormItem label="类型" {...this.formLayout}>
            {getFieldDecorator('typ', {
              initialValue: current.typ === undefined ? 'source-table' : current.typ,
              rules: [
                {
                  required: true,
                },
              ],
            })(<Input placeholder="请输入" disabled />)}
          </FormItem>
          <FormItem label="命名空间" {...this.formLayout}>
            {getFieldDecorator('namespaceId', {
              initialValue:
                current.namespaceId === undefined || current.namespaceId === null
                  ? 0
                  : current.namespaceId,
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
          <FormItem label="配置文件" {...this.formLayout}>
            <AceEditor
              mode="yaml"
              theme="solarized_dark"
              onChange={x => this.setState({ yaml: x })}
              name="functionConstructorConfig"
              editorProps={{ $blockScrolling: true }}
              readOnly={false}
              placeholder={'请输入Yaml配置'}
              defaultValue={this.state.yaml}
              value={this.state.yaml}
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
                  initialValue: current.isAvailable,
                  valuePropName: 'checked',
                })(<Switch checkedChildren="启用" unCheckedChildren="禁止" />)}
              </Col>
              <Col span={3}>
                {getFieldDecorator('isPublish', {
                  initialValue: current.isPublish,
                  valuePropName: 'checked',
                })(<Switch checkedChildren="发布" unCheckedChildren="开发" />)}
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
              title="文件列表"
              style={{ marginTop: 24 }}
              bodyStyle={{ padding: '0 32px 40px 32px' }}
              extra={extraContent}
            >
              {currentPage === 1 && (
                <Button
                  type="dashed"
                  style={{ width: '100%', marginBottom: 8 }}
                  icon="plus"
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
                dataSource={this.getAllData()}
                pagination={{
                  ...paginationProps,
                  pageSize: pageSize,
                  total: this.getAllData().length,
                  current: currentPage,
                }}
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
                      title={<a href="#">{item.name}</a>}
                      avatar={
                        <Avatar src={this.getAvar(item.namespaceId)} shape="square" size="large" />
                      }
                      description={item.info}
                    />
                    <ListContent data={item} />
                  </List.Item>
                )}
              />
            </Card>
          </div>
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
          {getModalContent(current.name === undefined)}
        </Modal>
      </>
    );
  }
}

export default Form.create<BasicListProps>()(BasicList);
