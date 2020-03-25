import React, { Component } from 'react';
import { findDOMNode } from 'react-dom';
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
  Modal,
  Row,
  Col,
  Switch,
  Select,
  Tag,
} from 'antd';
import { FormComponentProps } from '@ant-design/compatible/es/form';
import { FileResource, Functions } from '../data';
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

const FormItem = Form.Item;
const { Search } = Input;
import { AnyAction } from 'redux';
import { UploadFile } from 'antd/es/upload/interface';
import { UNIQUE_NAME_RULES } from '@/utils/UNIQUE_NAME_RULES';

interface BasicListProps extends FormComponentProps {
  listBasicList: Functions[];
  dispatch: Dispatch<AnyAction>;
  total: number;
  loading: boolean;
  resource: FileResource[];
}

interface BasicListState {
  visible: boolean;
  done: boolean;
  current?: Partial<Functions>;
  search: string;
  msg: string;
  success: boolean;
  submitted: boolean;
  fileList: UploadFile[];
  pageSize: number;
  currentPage: number;
}

@connect(
  ({
    functions,
    loading,
    total,
  }: {
    functions: { list: Functions[]; dependence: FileResource[] };
    loading: {
      models: { [key: string]: boolean };
    };
    total: number;
  }) => ({
    listBasicList: functions.list,
    loading: loading.models.file,
    resource: functions.dependence,
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
    const { dispatch } = this.props;
    dispatch({
      type: 'functions/fetch',
    });
  }

  showModal = () => {
    this.setState({
      visible: true,
      submitted: false,
      current: {},
      fileList: [],
    });
  };

  showEditModal = (item: Functions) => {
    this.setState({
      visible: true,
      current: item,
      submitted: false,
    });
  };
  onCodeChange = (value: string, event: Event) => {
    const old = this.state.current;
    const newCurrent = { ...old, constructorConfig: value };
    this.setState({ current: newCurrent });
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
    form.validateFields((err: string | undefined, fieldsValue: Functions) => {
      if (err) return;
      this.setState({ submitted: true });
      fieldsValue.constructorConfig =
        current && current.constructorConfig ? current.constructorConfig : '';

      dispatch({
        type: 'functions/submit',
        payload: { ...current, ...fieldsValue },
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
      type: 'functions/submit',
      payload: { id },
    });
  };

  onSearch = (value: string, event?: any) => {
    this.setState({ search: value, currentPage: 1 });
  };

  getFilterPageData = () => {
    const { search } = this.state;
    const { listBasicList } = this.props;
    return listBasicList.filter(x => x.name.indexOf(search) >= 0);
  };

  getCurrentPageData = () => {
    const { pageSize, currentPage } = this.state;
    const data = this.getFilterPageData();
    return data.slice((currentPage - 1) * pageSize, currentPage * pageSize);
  };

  onPageChange = (current: number, newPageSize: any) => {
    this.setState({ pageSize: newPageSize, currentPage: current });
  };

  getResourceName = (id: number) => {
    const { resource } = this.props;
    const data = resource.filter(x => x.id === id);
    return data.length > 0 ? data[0].uniqueName : '#';
  };

  render() {
    const { loading, resource } = this.props;
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

    const editAndDelete = (key: string, currentItem: Functions) => {
      if (key === 'edit') this.showEditModal(currentItem);
      else if (key === 'delete') {
        Modal.confirm({
          title: '删除任务',
          content: '确定删除该任务吗？',
          okText: '确认',
          cancelText: '取消',
          onOk: () => this.deleteItem(currentItem.id ? currentItem.id : 0),
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
        <Search
          defaultValue={search}
          className={styles.extraContentSearch}
          placeholder="请输入"
          onSearch={this.onSearch}
        />
      </div>
    );
    const ListContent = ({
      data: { name, className, isAvailable, isPublish, createAt, updateAt, resourceId },
    }: {
      data: Functions;
    }) => (
      <div className={styles.listContent}>
        <div className={styles.listContentItem}>
          <span>方法名</span>
          <p>
            <Tag>{name}</Tag>
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
            status={isAvailable ? (isPublish ? 'success' : 'normal') : 'exception'}
            strokeWidth={1}
            width={50}
            style={{ width: 180 }}
          />
        </div>
      </div>
    );

    const MoreBtn: React.SFC<{
      item: Functions;
    }> = ({ item }) => (
      <Dropdown
        overlay={
          <Menu onClick={({ key }) => editAndDelete(key, item)}>
            <Menu.Item key="delete">删除</Menu.Item>
          </Menu>
        }
      >
        <a>
          更多 <DownOutlined />
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

          <FormItem label="来源" {...this.formLayout}>
            {getFieldDecorator('functionFrom', {
              initialValue: 'class',
              rules: [
                {
                  required: true,
                },
              ],
            })(<Input placeholder="请输入" disabled />)}
          </FormItem>

          <FormItem label="类名" {...this.formLayout}>
            {getFieldDecorator('className', {
              initialValue: current.className,
              rules: [
                {
                  required: true,
                },
              ],
            })(<Input placeholder="请输入" />)}
          </FormItem>
          <FormItem label="文件" {...this.formLayout}>
            {getFieldDecorator('resourceId', {
              initialValue: current.resourceId,
              rules: [
                {
                  required: true,
                },
              ],
            })(
              <Select placeholder="请选择" size="large" style={{ width: 120 }}>
                {resource.length > 0 &&
                  resource.map((x: FileResource) => {
                    return (
                      <SelectOption key={x.id} value={x.id}>
                        {x.uniqueName}
                      </SelectOption>
                    );
                  })}
              </Select>,
            )}
          </FormItem>
          <FormItem label="构造器" {...this.formLayout}>
            <AceEditor
              mode="yaml"
              theme="solarized_dark"
              onChange={this.onCodeChange}
              name="functionConstructorConfig"
              editorProps={{ $blockScrolling: true }}
              readOnly={false}
              placeholder={'请输入Yaml配置'}
              defaultValue={
                current.constructorConfig === '' ? 'constructor:' : current.constructorConfig
              }
              value={current.constructorConfig}
              // width={'765'}
              // height={'650'}
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
                pagination={{
                  ...paginationProps,
                  pageSize: pageSize,
                  total: this.getFilterPageData().length,
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
                      title={<a href="#">{item.className}</a>}
                      description={this.getResourceName(item.resourceId)}
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
