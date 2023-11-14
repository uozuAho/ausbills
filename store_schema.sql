CREATE TABLE IF NOT EXISTS bill (
    id text unique,
    title text,
    link text,
    summary text,
    status text,
    parliament text,
    house text,
    passed_house boolean,
    passed_senate boolean,
    sponsor text
);

create table if not exists bill_summary_embedding (
    bill_id text unique,
    embedding blob
    -- no FK so we can keep expensive embeddings while deleting bills
);
