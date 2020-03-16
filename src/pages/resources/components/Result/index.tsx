import React from 'react';
import classNames from 'classnames';
import { CheckCircleFilled, CloseCircleFilled } from '@ant-design/icons';
import styles from './index.less';

export interface ResultProps {
  actions?: React.ReactNode;
  className?: string;
  description?: React.ReactNode;
  extra?: React.ReactNode;
  style?: React.CSSProperties;
  title?: React.ReactNode;
  type: 'success' | 'error' | 'line';
}

const Result: React.SFC<ResultProps> = ({
  className,
  type,
  title,
  description,
  extra,
  actions,
  ...restProps
}) => {
  const iconMap = {
    error: <CloseCircleFilled className={styles.error} />,
    success: <CheckCircleFilled className={styles.success} />,
  };
  const clsString = classNames(styles.result, className);
  return (
    <div className={clsString} {...restProps}>
      <div className={styles.icon}>{iconMap[type]}</div>
      <div className={styles.title}>{title}</div>
      {description && <pre style={{ textAlign: 'left' }}>{description}</pre>}
      {extra && <div className={styles.extra}>{extra}</div>}
      {actions && <div className={styles.actions}>{actions}</div>}
    </div>
  );
};

export default Result;
