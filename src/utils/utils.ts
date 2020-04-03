/* eslint no-useless-escape:0 import/prefer-default-export:0 */
const reg = /(((^https?:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+(?::\d+)?|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)((?:\/[\+~%\/.\w-_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?)$/;
const MAX_LENGTH = 13;

const isUrl = (path: string): boolean => {
  return reg.test(path);
};

const cutStr = (str?: string | null, len?: number): string => {
  return str === undefined || str === null
    ? ''
    : str.substring(0, len === undefined ? MAX_LENGTH : len);
};

const nullif = (v: any | null | undefined, t: any): any => {
  return v === undefined || v === null ? t : v;
};

const isAntDesignPro = (): boolean => {
  if (ANT_DESIGN_PRO_ONLY_DO_NOT_USE_IN_YOUR_PRODUCTION === 'site') {
    return true;
  }
  return window.location.hostname === 'preview.pro.ant.design';
};

// 给官方演示站点用，用于关闭真实开发环境不需要使用的特性
const isAntDesignProOrDev = (): boolean => {
  const { NODE_ENV } = process.env;
  if (NODE_ENV === 'development') {
    return true;
  }
  return isAntDesignPro();
};

export { isAntDesignProOrDev, isAntDesignPro, isUrl, MAX_LENGTH, cutStr, nullif };
