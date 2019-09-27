export const UNIQUE_NAME_RULES = [
  {
    message: '请输入称只能包含数字字母以及下划线(首字母必须为字母）',
    whitespace: true,
    required: true,
    pattern: /^[a-zA-Z][a-zA-Z0-9_]+/,
  },
  {
    message: '至少4位数',
    min: 4,
  },
  {
    message: '最长32位数',
    max: 32,
  },
];
