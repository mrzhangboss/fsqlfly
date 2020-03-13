import React from 'react';
import classNames from 'classnames';
import { CheckCircleFilled, CloseCircleFilled, CodeTwoTone } from '@ant-design/icons';
import styles from './index.less';

export interface ResultProps {
  actions?: React.ReactNode;
  className?: string;
  description?: React.ReactNode;
  extra?: React.ReactNode;
  style?: React.CSSProperties;
  title?: React.ReactNode;
  type: 'success' | 'error' | 'line';
  errorInfo?: string;
}

const Result: React.SFC<ResultProps> = ({
  className,
  type,
  title,
  description,
  extra,
  actions,
  errorInfo,
  ...restProps
}) => {
  const iconMap = {
    error: <CloseCircleFilled className={styles.error} />,
    success: <CheckCircleFilled className={styles.success} />,
    line: <CodeTwoTone />,
  };
  const clsString = classNames(styles.result, className);
  return (
    <div className={clsString} {...restProps}>
      <div className={styles.icon}>{iconMap[type]}</div>
      <div className={styles.title}>{title}</div>
      {description && <div className={styles.description}>{description}</div>}
      {errorInfo && <pre className={styles.code}>{errorInfo}</pre>}
      {extra && <div className={styles.extra}>{extra}</div>}
      {actions && <div className={styles.actions}>{actions}</div>}
    </div>
  );
};

export default Result;
