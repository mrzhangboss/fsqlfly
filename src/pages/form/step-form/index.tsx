import React, { Component, Fragment } from 'react';
import { Card, List, Steps } from 'antd';
import { connect } from 'dva';
import { PageHeaderWrapper } from '@ant-design/pro-layout';
import Step1 from './components/Step1';
import Step3 from './components/Step3';
import ListTransform from './components/ListTransform';
import styles from './style.less';
import { IStateType } from './models/stepModel';
import ModifyResource from './components/ModifyResource';

const { Step } = Steps;

interface StepFormProps {
  current: IStateType['current'];
  ready: boolean;
}

@connect(({ formStepForm }: { formStepForm: IStateType }) => ({
  current: formStepForm.current,
  ready: formStepForm.ready,
}))
class StepForm extends Component<StepFormProps> {
  getCurrentStep() {
    const { current } = this.props;
    switch (current) {
      case 'info':
        return 0;
      case 'confirm':
        return 1;
      case 'result':
        return 2;
      default:
        return -1;
    }
  }

  render() {
    const currentStep = this.getCurrentStep();
    const { ready } = this.props;
    let stepComponent;
    if (currentStep === 1) {
      stepComponent = (
        <div>
          <ModifyResource />
        </div>
      );
    } else if (currentStep === 2) {
      stepComponent = <Step3 />;
    } else if (currentStep === 0) {
      stepComponent = <Step1 />;
    } else {
      stepComponent = <ListTransform />;
    }
    return (
      <PageHeaderWrapper content="数据处理">
        <Card bordered={false}>
          <Fragment>
            {currentStep >= 0 && (
              <Steps current={currentStep} className={styles.steps}>
                <Step title="选择数据源" />
                <Step title="数据源配置" />
                <Step title="编写SQL" />
              </Steps>
            )}
            {!ready && <List loading={true} />}
            {ready && stepComponent}
          </Fragment>
        </Card>
      </PageHeaderWrapper>
    );
  }
}

export default StepForm;
