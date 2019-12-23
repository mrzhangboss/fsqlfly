interface TableField {
  name: string;
  typ: string;
  unique: boolean;
  primary: boolean;
}

interface TableMeta {
  name: string;
  info: string;
  tableName: string;
  namespace: string;
  fields: TableField[];
}

interface TableDetail {
  typ: string;
  show: boolean;
  loading: boolean;
  tableName: string;
  tableInfo: string;
  values:
    | Array<{ typ: string; name: string; value: string | number }>
    | Array<{ [key: string]: number | string }>;
  fields: Array<{ name: string; typ: 'number' | 'choose' | 'text' | 'date' | 'datetime' }>;
}

interface VisualizationResult {
  tables: TableMeta[];
  details: TableDetail[];
  search: string;
  limit: number;
  selectTable: string;
}
