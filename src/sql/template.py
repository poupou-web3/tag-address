sql_template = """
WITH
  transactions AS (
    SELECT
      BLOCK_TIMESTAMP,
      TX_FEE,
      FROM_ADDRESS AS EOA,
      TO_ADDRESS AS COUNTERPARTY,
      ETH_VALUE,
      1 as BOOLEAN_OUT
    FROM
      optimism.core.fact_transactions
    WHERE
      FROM_ADDRESS IN (%s)
    UNION ALL
    SELECT
      BLOCK_TIMESTAMP,
      TX_FEE,
      TO_ADDRESS AS EOA,
      TO_ADDRESS AS COUNTERPARTY,
      ETH_VALUE,
      0 as BOOLEAN_OUT
    FROM
      optimism.core.fact_transactions
    WHERE
      TO_ADDRESS IN (%s)
  )
SELECT
  EOA,
  COUNT(*) as n_tx,
  COUNT(DISTINCT(COUNTERPARTY)) as n_counterparty,
  SUM(ETH_VALUE) as eth_volume,
  SUM(BOOLEAN_OUT) as n_tx_out,
  n_tx - n_tx_out as n_tx_in,
  n_tx_out - n_tx_in as n_tx_diff_out_in,
  TIMESTAMPDIFF(MINUTE, MIN(BLOCK_TIMESTAMP), CURRENT_TIMESTAMP()) as age,
  TIMESTAMPDIFF(MINUTE, MIN(BLOCK_TIMESTAMP), MAX(BLOCK_TIMESTAMP)) as time_alive,
  CASE WHEN age = 0 THEN 0 ELSE n_tx / age END as tx_min,
  CASE WHEN time_alive = 0 THEN 0 ELSE n_tx / time_alive END as tx_min_alive,
  AVG(TX_FEE) as avg_tx_fee,
  STDDEV(TX_FEE) as std_tx_fee
FROM
  transactions
GROUP BY
  EOA;
"""


def get_sql_tx(table_name, eoa_list):
    sql = f"""
    SELECT
          BLOCK_TIMESTAMP,
          TX_FEE,
          FROM_ADDRESS AS EOA,
          TO_ADDRESS AS COUNTERPARTY,
          ETH_VALUE,
          1 as BOOLEAN_OUT
        FROM
          {table_name}
        WHERE
          FROM_ADDRESS IN ({eoa_list})
        UNION ALL
        SELECT
          BLOCK_TIMESTAMP,
          TX_FEE,
          TO_ADDRESS AS EOA,
          TO_ADDRESS AS COUNTERPARTY,
          ETH_VALUE,
          0 as BOOLEAN_OUT
        FROM
          {table_name}
        WHERE
          TO_ADDRESS IN ({eoa_list})
    """
    return sql


def get_sql_features_from(table_name):
    sql = f"""
    SELECT
      EOA,
      COUNT(*) as n_tx,
      COUNT(DISTINCT(COUNTERPARTY)) as n_counterparty,
      SUM(ETH_VALUE) as eth_volume,
      SUM(BOOLEAN_OUT) as n_tx_out,
      n_tx - n_tx_out as n_tx_in,
      n_tx_out - n_tx_in as n_tx_diff_out_in,
      TIMESTAMPDIFF(MINUTE, MIN(BLOCK_TIMESTAMP), CURRENT_TIMESTAMP()) as age,
      TIMESTAMPDIFF(MINUTE, MIN(BLOCK_TIMESTAMP), MAX(BLOCK_TIMESTAMP)) as time_alive,
      CASE WHEN age = 0 THEN 0 ELSE n_tx / age END as tx_min,
      CASE WHEN time_alive = 0 THEN 0 ELSE n_tx / time_alive END as tx_min_alive,
      AVG(TX_FEE) as avg_tx_fee,
      STDDEV(TX_FEE) as std_tx_fee
    FROM
      {table_name}
    GROUP BY
      EOA
    """
    return sql


def get_sql_template(table_name, eoa_list):
    sql = f"""
    WITH
      transactions AS (
        {get_sql_tx(table_name, eoa_list)}
      )
    {get_sql_features_from('transactions')}
    ;
    """
    return sql
