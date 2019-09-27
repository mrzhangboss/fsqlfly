import { Transfer, Table, Tag } from 'antd';
import difference from 'lodash/difference';
import * as React from 'react';
import { ResourceColumn } from '../../data';

const columns = [
  {
    dataIndex: 'name',
    title: 'Name',
  },
  {
    dataIndex: 'namespace',
    title: '命名空间',
    render: (tag: string) => {
      return <Tag>{tag}</Tag>;
    },
  },
  {
    dataIndex: 'info',
    title: 'Description',
  },
];
const TableTransfer = ({ ...restProps }) => (
  <Transfer {...restProps} showSelectAll={false}>
    {({
      direction,
      filteredItems,
      onItemSelectAll,
      onItemSelect,
      selectedKeys: listSelectedKeys,
      disabled: listDisabled,
    }) => {
      const rowSelection = {
        getCheckboxProps: (item: ResourceColumn) => ({
          disabled: item.disabled,
        }),
        onSelectAll(selected: any, selectedRows: any[]) {
          const treeSelectedKeys = selectedRows.filter(item => !item.enable).map(({ key }) => key);
          const diffKeys = selected
            ? difference(treeSelectedKeys, listSelectedKeys)
            : difference(listSelectedKeys, treeSelectedKeys);
          onItemSelectAll(diffKeys, selected);
        },
        onSelect({ key }: { key: any }, selected: any) {
          onItemSelect(key, selected);
        },
        selectedRowKeys: listSelectedKeys,
      };

      return (
        <Table
          //@ts-ignore
          rowSelection={rowSelection}
          columns={columns}
          dataSource={filteredItems}
          size="small"
          style={{ pointerEvents: listDisabled ? 'none' : 'all' }}
          //@ts-ignore
          onRow={({ key, disabled: itemDisabled }) => ({
            onClick: () => {
              if (itemDisabled || listDisabled) return;
              onItemSelect(key, !listSelectedKeys.includes(key));
            },
          })}
        />
      );
    }}
  </Transfer>
);

export default TableTransfer;
