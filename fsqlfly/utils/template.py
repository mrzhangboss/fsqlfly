from typing import Optional, Union
from datetime import timedelta, datetime
from fsqlfly.utils import macros


def generate_template_context(execution_date: Optional[Union[datetime, str]] = None, **kwargs):
    execution_date = execution_date if execution_date else datetime.now()
    if isinstance(execution_date, str):
        fmt = '%Y-%m-%d' if len(execution_date) == 10 else '%Y-%m-%d %H:%M:%S'
        execution_date = datetime.strptime(execution_date, fmt)
    ds = execution_date.strftime('%Y-%m-%d')
    ts = execution_date.isoformat()
    yesterday_ds = (execution_date - timedelta(1)).strftime('%Y-%m-%d')
    tomorrow_ds = (execution_date + timedelta(1)).strftime('%Y-%m-%d')

    ds_nodash = ds.replace('-', '')
    ts_nodash = execution_date.strftime('%Y%m%dT%H%M%S')
    ts_nodash_with_tz = ts.replace('-', '').replace(':', '')
    yesterday_ds_nodash = yesterday_ds.replace('-', '')
    tomorrow_ds_nodash = tomorrow_ds.replace('-', '')

    return {
        'ds': ds,
        'ds_nodash': ds_nodash,
        'ts': ts,
        'ts_nodash': ts_nodash,
        'ts_nodash_with_tz': ts_nodash_with_tz,
        'yesterday_ds': yesterday_ds,
        'yesterday_ds_nodash': yesterday_ds_nodash,
        'tomorrow_ds': tomorrow_ds,
        'tomorrow_ds_nodash': tomorrow_ds_nodash,
        'END_DATE': ds,
        'end_date': ds,
        'execution_date': execution_date,
        'latest_date': ds,
        'macros': macros,
        **kwargs
    }
