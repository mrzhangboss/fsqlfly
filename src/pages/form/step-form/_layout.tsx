import React from 'react';
import { he } from './style.less';
// import WarpForm from '../index';

const Layout: React.FC = ({ children }) => {
  return (
    <div>
      <h1 className={he}>GGGGG</h1>
      {/*<WarpForm formSearch={{ list: [] }}/>*/}

      {children}
    </div>
  );
};

export default Layout;
