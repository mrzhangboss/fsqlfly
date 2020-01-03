import { ButtonType } from 'antd/lib/button/button';

interface TableField {
  name: string;
  typ: string;
  unique: boolean;
  primary: boolean;
}

interface TableMeta {
  name: string;
  typ: 'kafka' | 'mysql' | 'hive';
  info?: string;
  tableName: string;
  namespace: string;
  fields: TableField[];
}

interface Field {
  name: string;
  typ: 'number' | 'string' | 'text' | 'date' | 'datetime';
  buttonType?: ButtonType;
}

interface TableDetail {
  typ: string;
  show: boolean;
  loading: boolean;
  tableName: string;
  search: string;
  limit: number;
  isEmpty: boolean;
  data: Array<{ [key: string]: number | string }>;
  fieldNames: Array<string>;
}

interface TableShortCut {
  tableName: string;
  search: string;
  limit: number;
  typ: string;
  visible: boolean;
}

interface TabTables {
  search: string;
  limit: number;
  selectTable: string;
  selectRelatedTableKeys: string[];
  relatedTables: TableMeta[];
  currentDisplayTables: TableShortCut[];
  current?: TableDetail;
}

interface VisualizationResult {
  tables: TableMeta[];
  relatedTables: TableMeta[];
  selectRelatedTableKeys: string[];
  currentDisplayTables: string[];
  details: TableDetail[];
  current?: TableDetail;
  search: string;
  limit: number;
  selectTable: string;
  errorDisplay: boolean;
  errorMsg: string;
  errorCode: number;
}
