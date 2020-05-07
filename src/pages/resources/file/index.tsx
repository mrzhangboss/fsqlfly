import React, { Component } from 'react';
import { findDOMNode } from 'react-dom';
import moment from 'moment';
import { connect } from 'dva';
import { DownOutlined, PlusOutlined, UploadOutlined } from '@ant-design/icons';
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
  Upload,
  Tooltip,
} from 'antd';
import { FormComponentProps } from '@ant-design/compatible/es/form';
import { Dispatch } from 'redux';
import { FileResource } from '../data';
import Result from '../components/Result';
import { PageHeaderWrapper } from '@ant-design/pro-layout';
import { cutStr, getStatus } from '@/utils/utils';

import styles from '../style.less';

const FormItem = Form.Item;
const { Search, TextArea } = Input;
import { AnyAction } from 'redux';
import { UploadFile } from 'antd/es/upload/interface';
import { UNIQUE_NAME_RULES } from '@/utils/UNIQUE_NAME_RULES';

interface BasicListProps extends FormComponentProps {
  listBasicList: FileResource[];
  dispatch: Dispatch<AnyAction>;
  total: number;
  loading: boolean;
}

interface BasicListState {
  visible: boolean;
  done: boolean;
  current?: Partial<FileResource>;
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
    loading,
    total,
    file,
  }: {
    loading: {
      models: { [key: string]: boolean };
    };
    total: number;
    file: { list: FileResource[] };
  }) => ({
    listBasicList: file.list,
    loading: loading.models.file,
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
      type: 'file/fetch',
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

  showEditModal = (item: FileResource) => {
    this.setState({
      visible: true,
      current: item,
      submitted: false,
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
    const { current, fileList } = this.state;

    setTimeout(() => this.addBtn && this.addBtn.blur(), 0);
    form.validateFields(
      (err: string | undefined, fieldsValue: FileResource & { upload: object }) => {
        if (err) return;
        this.setState({ submitted: true });
        // @ts-ignore
        if (fieldsValue.upload !== undefined) {
          fieldsValue.realPath = fileList[0].response.data.realPath;
          delete fieldsValue.upload;
        }
        dispatch({
          type: 'file/submit',
          payload: { ...(current ? current : {}), ...fieldsValue },
          callback: (res: { success: boolean; msg: string }) => {
            this.setState({
              done: true,
              success: res.success,
              msg: res.msg,
            });
          },
        });
      },
    );
  };

  deleteItem = (id: number) => {
    // @ts-ignore
    const { dispatch } = this.props;
    dispatch({
      type: 'file/submit',
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

  render() {
    const { loading } = this.props;
    const {
      form: { getFieldDecorator },
    } = this.props;

    const {
      visible,
      done,
      current = {},
      search,
      fileList,
      success,
      msg,
      submitted,
      pageSize,
      currentPage,
    } = this.state;

    const editAndDelete = (key: string, currentItem: FileResource) => {
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
          onSearch={x => this.setState({ search: x })}
        />
      </div>
    );
    const ListContent = ({
      data: { name, info, isActive, isLocked, createAt, updateAt },
    }: {
      data: FileResource;
    }) => (
      <div className={styles.listContent}>
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

    const MoreBtn: React.SFC<{
      item: FileResource;
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

          <FormItem label="介绍" {...this.formLayout}>
            {getFieldDecorator('info', {
              initialValue: current.info,
            })(<TextArea placeholder="请输入" />)}
          </FormItem>
          <FormItem label="文件" {...this.formLayout}>
            {getFieldDecorator('upload', {
              valuePropName: 'fileList',
              getValueFromEvent: this.normFile,
              initialValue: fileList,
              rules: [
                {
                  required: true,
                  message: '文件必须存在',
                },
              ],
            })(
              <Upload
                name="file"
                action="/api/upload"
                fileList={fileList}
                onChange={e => this.setState({ fileList: e.fileList })}
              >
                {fileList.length === 1 ? null : (
                  <Button>
                    <UploadOutlined /> {isCreate ? '点击上传' : '点击替换文件'}
                  </Button>
                )}
              </Upload>,
            )}
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
                dataSource={this.getCurrentPageData()}
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
                      title={
                        <Tooltip title={item.name} placement="right">
                          <span>
                            <a href="#">{cutStr(item.name)}</a>
                          </span>
                        </Tooltip>
                      }
                      description={
                        <Tooltip title={item.info + ' : ' + item.realPath} placement="right">
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
