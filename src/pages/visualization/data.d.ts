interface TableField {
  name: string;
  typ: string;
  unique: boolean;
  primary: boolean;
}

interface TableMeta {
  name: string;
  tableName: string;
  namespace: string;
  fields: TableField[];
}

interface VisualizationResult {
  tables: TableMeta[];
}
