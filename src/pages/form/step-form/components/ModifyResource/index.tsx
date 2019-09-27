import React, { Component } from 'react';
import { connect } from 'dva';
import {
  List,
  Card,
  Input,
  Button,
  Icon,
  Dropdown,
  Menu,
  Avatar,
  Modal,
  Form,
  Tag,
  Select,
} from 'antd';
import { FormComponentProps } from 'antd/es/form';
import { Dispatch } from 'redux';
import { ResourceColumn } from '../../data';
import Result from '../Result';
import styles from '@/pages/resources/style.less';

const FormItem = Form.Item;
const { Search } = Input;
import { AnyAction } from 'redux';

interface BasicListProps extends FormComponentProps {
  listBasicList: ResourceColumn[];
  dispatch: Dispatch<AnyAction>;
  loading: boolean;
}

interface BasicListState {
  visible: boolean;
  done: boolean;
  current?: Partial<ResourceColumn>;
  search: string;
  msg: string;
  success: boolean;
  submitted: boolean;
}

class BasicList extends Component<BasicListProps, BasicListState> {
  state: BasicListState = {
    visible: false,
    done: false,
    current: {},
    search: '',
    msg: '',
    success: false,
    submitted: false,
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
      type: 'formStepForm/initSourceColumn',
    });
  }

  showModal = () => {
    this.setState({
      visible: true,
      submitted: false,
      current: {},
    });
  };

  showEditModal = (item: ResourceColumn) => {
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
    const { current } = this.state;

    setTimeout(() => this.addBtn && this.addBtn.blur(), 0);
    form.validateFields(
      (
        err: string | undefined,
        fieldsValue: ResourceColumn & {
          upload: Array<{ response: string }>;
          type: string;
        },
      ) => {
        if (err) return;
        this.setState({ submitted: true });
        dispatch({
          type: 'formStepForm/updateColumnTable',
          payload: {
            id: current ? current.id : 0,
            rowtime: fieldsValue.rowtime,
            proctime: fieldsValue.proctime,
          },
        });
        this.setState({
          done: true,
          success: true,
          msg: '修改完成',
        });
      },
    );
  };

  deleteItem = (id: number) => {
    // @ts-ignore
    const { dispatch } = this.props;
    dispatch({
      type: 'formStepForm/deleteColumnTable',
      id,
    });
  };

  onSearch = (value: string, event?: any) => {
    this.setState({ search: value });
    const { dispatch } = this.props;
    dispatch({
      type: 'targetModel/fetch',
      payload: {
        search: value,
      },
    });
  };

  render() {
    const { dispatch } = this.props;
    const onPrev = () => {
      if (dispatch) {
        dispatch({
          type: 'formStepForm/updateColumnDetail',
          payload: listBasicList,
        });
        dispatch({
          type: 'formStepForm/saveCurrentStep',
          payload: 'info',
        });
      }
    };
    const onValidateForm = (e: React.FormEvent) => {
      e.preventDefault();
      dispatch({
        type: 'formStepForm/updateColumnDetail',
        payload: listBasicList,
      });
      dispatch({
        type: 'formStepForm/saveCurrentStep',
        payload: 'result',
      });
    };
    const { listBasicList, loading } = this.props;
    const {
      form: { getFieldDecorator },
    } = this.props;

    const { visible, done, current = {}, search, success, msg, submitted } = this.state;

    const editAndDelete = (key: string, currentItem: ResourceColumn) => {
      if (key === 'edit') this.showEditModal(currentItem);
      else if (key === 'delete') {
        Modal.confirm({
          title: '删除任务',
          content: '确定删除该任务吗？',
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
            <Button
              key="submit"
              type="primary"
              loading={submitted}
              onClick={current.name === undefined ? this.handleSubmit : this.handleUpdate}
            >
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
      data: { name, info, rowtime, proctime, namespace },
    }: {
      data: ResourceColumn;
    }) => (
      <div className={styles.listContent}>
        <div className={styles.listContentItem}>
          <span>rowtime</span>
          <p>{rowtime}</p>
        </div>
        <div className={styles.listContentItem}>
          <span>proctime</span>
          <p>{proctime}</p>
        </div>
        <div className={styles.listContentItem}>
          <Tag>{namespace}</Tag>
        </div>
      </div>
    );

    const MoreBtn: React.SFC<{
      item: ResourceColumn;
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
      const SelectOption = Select.Option;
      // @ts-ignore
      return (
        <Form onSubmit={isCreate ? this.handleSubmit : this.handleUpdate}>
          <FormItem label="rowtime" {...this.formLayout}>
            {getFieldDecorator('rowtime', {
              rules: [
                {
                  message:
                    '请输入3-32的唯一名称只能包含数字字母以及下划线(首字母必须为字母）为空默认不使用',
                  whitespace: true,
                  min: 3,
                  max: 32,
                  pattern: /[a-zA-Z][a-zA-Z0-9_]+/,
                },
              ],
              initialValue: current.rowtime,
            })(
              <Select placeholder="请选择" size="default" style={{ width: 120 }}>
                <SelectOption key="-----empty" value="">
                  不使用
                </SelectOption>
                {this.state.current &&
                  this.state.current.columns &&
                  this.state.current.columns.length > 0 &&
                  this.state.current.columns.map(x => {
                    return (
                      <SelectOption key={x.id} value={x.name}>
                        {x.name}
                      </SelectOption>
                    );
                  })}
              </Select>,
            )}
          </FormItem>

          <FormItem label="processTime" {...this.formLayout}>
            {getFieldDecorator('proctime', {
              rules: [
                {
                  message:
                    '请输入3-32的唯一名称只能包含数字字母以及下划线(首字母必须为字母）为空默认不使用',
                  whitespace: true,
                  min: 3,
                  max: 32,
                  pattern: /[a-zA-Z][a-zA-Z0-9_]+/,
                },
              ],
              initialValue: current.proctime,
            })(<Input placeholder="请输入" />)}
          </FormItem>
        </Form>
      );
    };
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
            <List
              size="large"
              rowKey="id"
              loading={loading}
              dataSource={listBasicList}
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
                    avatar={<Avatar src={item.avatar} shape="square" size="large" />}
                    title={<a href={item.avatar}>{item.name}</a>}
                    description={item.info}
                  />
                  <ListContent data={item} />
                </List.Item>
              )}
            />
          </Card>

          <Button type="primary" onClick={onValidateForm} loading={loading}>
            下一步
          </Button>
          <Button onClick={onPrev} style={{ marginLeft: 8 }}>
            上一步
          </Button>
        </div>

        <Modal
          title={done ? null : `任务${current ? '编辑' : '添加'}`}
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

const finalForm = Form.create<BasicListProps>()(BasicList);

export default connect(
  ({
    formStepForm,
    loading,
  }: {
    formStepForm: { detailColumns: ResourceColumn[] };
    loading: {
      models: { [key: string]: boolean };
    };
  }) => ({
    listBasicList: formStepForm.detailColumns,
    loading: loading.models.namespace,
  }),
)(finalForm);
