import React, { Fragment } from 'react';
import { connect } from 'dva';
import { Button, Checkbox, Divider, Input, Modal, Select } from 'antd';
import Result from '../Result';
import styles from './index.less';
import { IStateType } from '../../models/stepModel';
import { Dispatch } from 'redux';
import AceEditor from 'react-ace';
import 'brace/mode/transform';
import 'brace/mode/yaml';
import 'brace/theme/solarized_dark';
import 'brace/theme/github';
import { Form } from 'antd';
import { FormComponentProps } from 'antd/es/form';
import { TransformInfo } from '@/pages/form/step-form/data';
import { UNIQUE_NAME_RULES } from '@/utils/UNIQUE_NAME_RULES';

const { TextArea } = Input;

interface Step3Props extends FormComponentProps {
  data?: TransformInfo;
  namespaces: { name: string; id: number }[];
  dispatch: Dispatch<any>;
}

interface StepState {
  isAvailable: boolean;
  isPublish: boolean;
  sql: string;
  name: string;
  info: string;
  namespaceId: number;
  config?: string;
  id?: number;
  submitted: boolean;
  done: boolean;
  success: boolean;
  msg: string;
}

class Step3 extends React.Component<Step3Props, StepState> {
  state = {
    sql: '',
    config: '',
    isAvailable: true,
    isPublish: false,
    name: '',
    info: '',
    submitted: false,
    success: true,
    msg: '',
    done: false,
    namespaceId: 0,
  };

  componentDidMount() {
    const { data } = this.props;
    if (data === undefined) return;
    // @ts-ignore
    this.setState({
      sql: data.sql,
      config: data.config,
      isAvailable: data.isAvailable,
      isPublish: data.isPublish,
      name: data.name,
      namespaceId: data.namespaceId,
      info: data.info,
      done: false,
      submitted: false,
    });
  }

  render() {
    const { data = this.state, dispatch } = this.props;
    const {
      form: { getFieldDecorator },
    } = this.props;
    const onPrev = () => {
      const { form } = this.props;

      const { sql, config } = this.state;
      const payload = { ...data, ...form.getFieldsValue(), sql, config };
      dispatch({
        type: 'formStepForm/saveStepFormData',
        payload,
      });
      dispatch({
        type: 'formStepForm/saveCurrentStep',
        payload: 'info',
      });
    };
    if (!data) {
      return;
    }

    const onCancel = () => {
      if (dispatch) {
        dispatch({
          type: 'formStepForm/saveCurrentStep',
          payload: 'list',
        });
      }
    };

    const conSubmit = () => {
      const { form } = this.props;
      const { sql, config } = this.state;
      form.validateFields((err: string | undefined, fieldsValue: any) => {
        if (err) return;
        this.setState({ submitted: true });
        dispatch({
          type: 'formStepForm/submitTransformTable',
          payload: {
            ...data,
            ...fieldsValue,
            sql,
            config,
          },
          callback: (res: { success: boolean; msg: string }) =>
            this.setState({
              success: res.success,
              msg: res.msg,
              submitted: false,
              done: true,
            }),
        });
      });
    };
    const debugSubmit = () => {
      const { form } = this.props;
      const { sql, config } = this.state;
      form.validateFields((err: string | undefined, fieldsValue: any) => {
        if (err) return;
        this.setState({ submitted: true });
        dispatch({
          type: 'formStepForm/submitDebugTransformTable',
          payload: {
            ...data,
            ...fieldsValue,
            sql,
            config,
          },
          callback: (res: { success: boolean; msg: string; data: { url: string } }) => {
            this.setState({
              submitted: false,
            });
            if (res.success) {
              window.open(res.data.url);
            }
          },
        });
      });
    };
    const FormItem = Form.Item;
    const SelectOption = Select.Option;
    const { namespaces } = this.props;
    // @ts-ignore
    // @ts-ignore
    const information = (
      <Form onSubmit={conSubmit}>
        <div className={styles.information}>
          {getFieldDecorator('isAvailable', {
            valuePropName: 'checked',
            initialValue: data.isAvailable,
          })(
            <Checkbox onChange={x => this.setState({ isAvailable: x.target.checked })}>
              是否可用
            </Checkbox>,
          )}

          {getFieldDecorator('isPublish', {
            valuePropName: 'checked',
            initialValue: data.isPublish,
          })(<Checkbox>是否发布</Checkbox>)}
          <FormItem label="name">
            <div>
              {getFieldDecorator('name', {
                initialValue: data.name,
                rules: UNIQUE_NAME_RULES,
              })(<Input placeholder="请输入名字" style={{ marginTop: 10, marginBottom: 10 }} />)}
            </div>
          </FormItem>
          <div>
            {//@ts-ignore
            getFieldDecorator('info', { initialValue: data.info })(
              <TextArea placeholder="请输入介绍" style={{ marginTop: 10, marginBottom: 10 }} />,
            )}
          </div>
          <FormItem label="命名空间">
            {getFieldDecorator('namespaceId', {
              initialValue: this.state.namespaceId,
              rules: [
                {
                  required: true,
                },
              ],
            })(
              <Select placeholder="请选择" size="default" style={{ width: 120 }}>
                <SelectOption value={0}>默认</SelectOption>
                {namespaces &&
                  namespaces.map((x: { name: string; id: number }) => {
                    return (
                      <SelectOption key={x.id} value={x.id}>
                        {x.name}
                      </SelectOption>
                    );
                  })}
              </Select>,
            )}
          </FormItem>
          <AceEditor
            mode="sql"
            theme="github"
            onChange={x => this.setState({ sql: x })}
            name="functionConstructorSQL"
            editorProps={{ $blockScrolling: true }}
            readOnly={false}
            placeholder={'your SQL'}
            //@ts-ignore
            value={this.state.sql}
            defaultValue={this.state.sql}
            width={'1036'}
          />
          <Divider style={{ margin: '40px 0 24px' }} />
          <AceEditor
            mode="yaml"
            theme="solarized_dark"
            onChange={x => this.setState({ config: x })}
            name="functionConstructorConfig"
            editorProps={{ $blockScrolling: true }}
            readOnly={false}
            value={this.state.config}
            placeholder={'your sink schema'}
            //@ts-ignore
            defaultValue={this.state.config}
            width={'1036'}
          />
        </div>
      </Form>
    );
    // @ts-ignore
    const submitName = data.id === undefined ? '创建' : '修改';
    const { submitted, success, msg, done } = this.state;
    const handleDone = () => {
      if (success) {
        dispatch({
          type: 'formStepForm/saveCurrentStep',
          payload: 'list',
        });
      } else {
        this.setState({ done: false });
      }
    };
    const actions = (
      <Fragment>
        <Button type="primary" onClick={onCancel}>
          取消
        </Button>
        <Button type="primary" onClick={conSubmit} loading={submitted}>
          {submitName}
        </Button>
        <Button type="primary" onClick={debugSubmit} loading={submitted}>
          调试
        </Button>
        <Button onClick={onPrev}>上一步</Button>
      </Fragment>
    );
    return (
      <>
        {done && (
          <Modal
            title="已完成"
            width={1080}
            bodyStyle={done ? { padding: '72px 0' } : { padding: '28px 0 0' }}
            destroyOnClose
            footer={null}
            onCancel={handleDone}
            visible
          >
            <Result
              type={success ? 'success' : 'error'}
              title={`${success ? '成功' : '失败'}`}
              description={success ? '' : msg}
              actions={
                <Button type="primary" onClick={handleDone}>
                  知道了
                </Button>
              }
              className={styles.formResult}
            />
          </Modal>
        )}
        {!done && (
          <Result
            type="line"
            title="数据处理"
            description=""
            extra={information}
            actions={actions}
          />
        )}
      </>
    );
  }
}

const Out = Form.create<Step3Props>()(Step3);
export default connect(
  ({
    formStepForm,
    loading,
  }: {
    formStepForm: IStateType;
    loading: {
      effects: { [key: string]: boolean };
    };
  }) => ({
    submitting: loading.effects['formStepForm/submitStepForm'],
    data: formStepForm.detail,
    namespaces: formStepForm.namespaces,
  }),
)(Out);
