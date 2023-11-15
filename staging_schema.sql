CREATE TABLE IF NOT EXISTS bill(id text, data json, error text);

-- summaries of bill summaries
create table if not exists bill_summary_summary(
    bill_id text unique,
    summary text,
    error text
);
