import React, { Fragment } from 'react';
import { connect } from 'dva';
import { Form, Button, Divider } from 'antd';
import { ResourceInfo } from '../../data';
import { FormComponentProps } from 'antd/es/form';
import { Dispatch } from 'redux';
import { TransferItem } from 'antd/es/transfer';
import TableTransfer from './TableTransfer';
import { ResourceColumn } from '@/pages/form/step-form/data';

interface Step1Props extends FormComponentProps {
  data?: ResourceInfo;
  dispatch: Dispatch<any>;
  sources: ResourceColumn[];
  targets: string[];
}

interface StepState {
  selectedKeys: string[];
}

class Step1 extends React.PureComponent<Step1Props, StepState> {
  state = {
    selectedKeys: [],
  };

  onChange = (nextTargetKeys: string[]) => {
    const { dispatch } = this.props;
    dispatch({
      type: 'formStepForm/updateTarget',
      payload: nextTargetKeys,
    });
  };

  componentDidMount() {
    // @ts-ignore
    const { dispatch } = this.props;
    dispatch({
      type: 'ListModel/fetch',
    });
  }

  render() {
    const { dispatch, data, sources, targets } = this.props;
    if (!data) {
      return;
    }

    const nextStep = () => {
      dispatch({
        type: 'formStepForm/saveCurrentStep',
        payload: 'result',
      });
    };
    const backToList = () => {
      if (!dispatch) return;
      dispatch({
        type: 'formStepForm/saveCurrentStep',
        payload: 'list',
      });
    };

    const isAllMatch = (s: string, namespace: string, name: string): boolean => {
      if (s === null || s.trim().length == 0 || name === null) return false;
      const v = /(?:ta?g?:)(\w+)\s/.exec(s);
      if (v !== null && namespace !== undefined) {
        const tagMatch = namespace.indexOf(v[1]) !== -1;
        const left = /(?:ta?g?:)\w+\s+(\w+)/.exec(s);
        if (left !== null) {
          return name.indexOf(left[1]) !== -1;
        } else {
          return tagMatch;
        }
      }
      if (v === null) {
        return name.indexOf(s.trim()) !== -1;
      }
      return false;
    };
    const filterSearch = (inputValue: string, item: TransferItem) => {
      return isAllMatch(inputValue, item.namespace, item.name);
    };
    return (
      <Fragment>
        <div>
          <TableTransfer
            showSearch
            searchPlaceholder={'支持命名空间过滤，搜索 例如输入tag:xxx 或者t:xxx 即可过滤'}
            showSelectAll
            dataSource={sources}
            titles={['Source', 'Target']}
            targetKeys={targets}
            selectedKeys={this.state.selectedKeys}
            onChange={this.onChange}
            onSelectChange={(sourceSelectedKeys: string[], targetSelectedKeys: string[]) =>
              this.setState({
                selectedKeys: [...sourceSelectedKeys, ...targetSelectedKeys],
              })
            }
            filterOption={filterSearch}
            rowKey={(x: ResourceColumn) => x.id}
          />
        </div>
        <Divider style={{ margin: '40px 0 24px' }} />

        <Button type="primary" onClick={nextStep}>
          下一步
        </Button>
        <Button
          type="default"
          onClick={backToList}
          style={{
            marginLeft: 8,
          }}
        >
          返回列表
        </Button>
      </Fragment>
    );
  }
}

export default connect(
  ({
    formStepForm,
  }: {
    formStepForm: ResourceInfo & {
      targetKeys: string[];
      resourceColumns: ResourceColumn[];
    };
  }) => ({
    data: formStepForm,
    sources: formStepForm.resourceColumns,
    targets: formStepForm.targetKeys,
  }),
)(Form.create<Step1Props>()(Step1));
