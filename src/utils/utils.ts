/* eslint no-useless-escape:0 import/prefer-default-export:0 */
const reg = /(((^https?:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+(?::\d+)?|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)((?:\/[\+~%\/.\w-_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?)$/;
const MAX_LENGTH = 13;

const isUrl = (path: string): boolean => {
  return reg.test(path);
};

const getStatus = (isActive: boolean, isLocked: boolean) => {
  return isActive ? (isLocked ? 'normal' : 'success') : 'exception';
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

// ['hive', 'db', 'kafka', 'hbase', 'elasticsearch', 'canal', 'file']

const CONNECTION_TEMPLATE = {
  hive: `type: hive
hive-conf-dir: /opt/hive-conf  # contains hive-site.xml
hive-version: 2.3.4`,
  kafka: `type: kafka
version: universal     # required: valid connector versions are    "0.8", "0.9", "0.10", "0.11", and "universal"
properties:
  zookeeper.connect: localhost:2181  # required: specify the ZooKeeper connection string
  bootstrap.servers: localhost:9092  # required: specify the Kafka server connection string
  group.id: testGroup                # optional: required in Kafka consumer, specify consumer group
topic: {{ resource_name.database }}__{{ resource_name.name }}
`,
  elasticsearch: `type: elasticsearch
version: 7                                            # required: valid connector versions are "6" "7"
hosts: http://host_name:9092;http://host_name:9093  # required: one or more Elasticsearch hosts to connect to
key-delimiter: "$"      # optional: delimiter for composite keys ("_" by default)    e.g., "$" would result in IDs "KEY1$KEY2$KEY3"
key-null-literal: "n/a" # optional: representation for null fields in keys ("null" by default)

# optional: failure handling strategy in case a request to Elasticsearch fails ("fail" by default)
failure-handler: fail    # valid strategies are "fail" (throws an exception if a request fails and
                            #   thus causes a job failure), "ignore" (ignores failures and drops the request),
                            #   "retry-rejected" (re-adds requests that have failed due to queue capacity
                            #   saturation), or "custom" for failure handling with a
                            #   ActionRequestFailureHandler subclass

# optional: configure how to buffer elements before sending them in bulk to the cluster for efficiency
flush-on-checkpoint: true   # optional: disables flushing on checkpoint (see notes below!) ("true" by default)
bulk-flush:
  max-actions: 42           # optional: maximum number of actions to buffer for each bulk request
  max-size: 42 mb           # optional: maximum size of buffered actions in bytes per bulk request
                            #   (only MB granularity is supported)
  interval: 60000           # optional: bulk flush interval (in milliseconds)
  back-off:                 # optional: backoff strategy ("disabled" by default)
    type: ...               #   valid strategies are "disabled", "constant", or "exponential"
    max-retries: 3          # optional: maximum number of retries
    delay: 30000            # optional: delay between each backoff attempt (in milliseconds)
`,
  hbase: `type: hbase
version: "1.4.3"               # required: currently only support "1.4.3"

table-name: "hbase_table_name" # required: HBase table name

zookeeper:
  quorum: "localhost:2181"     # required: HBase Zookeeper quorum configuration
  znode.parent: "/test"        # optional: the root dir in Zookeeper for HBase cluster.
                               # The default value is "/hbase".

write.buffer-flush:
  max-size: "10mb"             # optional: writing option, determines how many size in memory of buffered
                               # rows to insert per round trip. This can help performance on writing to JDBC
                               # database. The default value is "2mb".
  max-rows: 1000               # optional: writing option, determines how many rows to insert per round trip.
                               # This can help performance on writing to JDBC database. No default value,
                               # i.e. the default flushing is not depends on the number of buffered rows.
  interval: "2s"               # optional: writing option, sets a flush interval flushing buffered requesting
                               # if the interval passes, in milliseconds. Default value is "0s", which means
                               # no asynchronous flush thread will be scheduled.`,
  db: `type: jdbc
url: "jdbc:mysql://localhost:3306/{{ resource_name.database }}"     # required: JDBC DB url
driver: "com.mysql.jdbc.Driver" # optional: the class name of the JDBC driver to use to connect to this URL.
                                # If not set, it will automatically be derived from the URL.
username: "name"                # optional: jdbc user name and password
password: "password"

table: "{{ resource_name.name }}"

                            # the hint is ignored. The default value is zero.

lookup: # lookup options, optional, used in temporary join
  cache:
    max-rows: 5000 # optional, max number of rows of lookup cache, over this value, the oldest rows will
                   # be eliminated. "cache.max-rows" and "cache.ttl" options must all be specified if any
                   # of them is specified. Cache is not enabled as default.
    ttl: "10s"     # optional, the max time to live for each rows in lookup cache, over this time, the oldest rows
                   # will be expired. "cache.max-rows" and "cache.ttl" options must all be specified if any of
                   # them is specified. Cache is not enabled as default.
  max-retries: 3   # optional, max retry times if lookup database failed

write: # sink options, optional, used when writing into table
    flush:
      max-rows: 5000 # optional, flush max size (includes all append, upsert and delete records),
                     # over this number of records, will flush data. The default value is "5000".
      interval: "2s" # optional, flush interval mills, over this time, asynchronous threads will flush data.
                     # The default value is "0s", which means no asynchronous flush thread will be scheduled.
    max-retries: 3   # optional, max retry times if writing records to database failed.

`,

  file: `type: filesystem
path: "file:///path/to/whatever"`,
  canal: `[canal]
canal_host: localhost
canal_port: 11111
canal_username: root
canal_password: password
canal_client_id: 11021
canal_destination: example
canal_filter: .*\\..*`,
};
const base = `include: .*\\.*
exclude:
schema:

`;
const kafkaSource = `include: .*\\.*
exclude:
schema:
  - name: flink_process_time
    data-type: TIMESTAMP
    proctime: true
  - name: rowTime
    data-type: TIMESTAMP(3)
    rowtime:
      timestamps:
        type: "from-field"
        from: "rideTime"
      watermarks:
        type: "periodic-bounded"
        delay: "60000"
`;
const view = `query: >
      SELECT MyField2 + 42, CAST(MyField1 AS VARCHAR)
      FROM MyTableSource
      WHERE MyField2 > 200
`;
const temporalTable = `history-table: HistorySource
primary-key: integerField
time-attribute: rowtimeField  # could also be a proctime field
`;

const TABLE_TYPE_TEMPLATE = {
  sink: base,
  source: base,
  both: base,
  kafka_sink: base,
  kafka_source: kafkaSource,
  kafka_both: base,
  view,
  'temporal-table': temporalTable,
};

export {
  isAntDesignProOrDev,
  isAntDesignPro,
  isUrl,
  MAX_LENGTH,
  cutStr,
  nullif,
  CONNECTION_TEMPLATE,
  TABLE_TYPE_TEMPLATE,
  getStatus,
};
