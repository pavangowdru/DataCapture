curl -X POST http://localhost:8093/connectors \
-H "Content-Type: application/json" \
-d '{
  "name": "postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "postgres",
    "database.password": "postgres",
    "database.dbname": "financial_db",
    "database.server.name": "financial-server",
    "topic.prefix": "cdc",
    "plugin.name": "pgoutput",
    "slot.name": "debezium_slot",
    "table.include.list": "public.transactions_copy",
    "publication.name": "dbz_publication"
  }
}'

#open interactive terminal for docker container
docker exec -it postgres

#Log into postgres
psql -U postgres -d financial_db

# Logs the entire row before any UPDATE or DELETE. Needed for debzium to capture before and after changes.
ALTER TABLE transactions_copy REPLICA IDENTITY FULL;

#Creating a trigger to add who has made changes at what time

ALTER TABLE transactions_copy
ADD COLUMN IF NOT EXISTS modified_by TEXT,
ADD COLUMN IF NOT EXISTS modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

CREATE OR REPLACE FUNCTION record_change_user()
RETURNS TRIGGER AS $$
BEGIN
NEW.modified_by := COALESCE(current_user, 'unknown');
NEW.modified_at := CURRENT_TIMESTAMP;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_modified_user
BEFORE INSERT OR UPDATE ON transactions_copy
FOR EACH ROW
EXECUTE FUNCTION record_change_user();


drop trigger set_modified_user on transactions_copy;

CREATE OR REPLACE FUNCTION record_changed_column()
RETURNS TRIGGER AS $$
DECLARE
    change_details JSONB;
BEGIN
    -- Initialize JSONB object
    change_details := '{}'::JSONB;

    -- Check if user_id has changed
    IF NEW.user_id IS DISTINCT FROM OLD.user_id THEN
        change_details := change_details || jsonb_build_object('user_id', jsonb_build_object('old', OLD.user_id, 'new', NEW.user_id));
    END IF;

    -- Add metadata fields
    change_details := change_details || jsonb_build_object('modified_by', current_user, 'modified_at', now());

    -- Assign to NEW.change_info
    NEW.change_info := change_details;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

ALTER TABLE transactions_copy
ADD COLUMN IF NOT EXISTS change_info JSONB;

CREATE TRIGGER set_modified_column
BEFORE UPDATE ON transactions_copy
FOR EACH ROW
EXECUTE FUNCTION record_changed_column();
