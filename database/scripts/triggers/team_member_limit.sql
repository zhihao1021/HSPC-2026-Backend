CREATE OR REPLACE FUNCTION enforce_team_member_limit()
RETURNS TRIGGER AS $$
DECLARE
	member_count INTEGER;
BEGIN
	IF NEW.team_id IS NULL THEN
		RETURN NEW;
	END IF;

	IF TG_OP = 'UPDATE' AND NEW.team_id = OLD.team_id THEN
		RETURN NEW;
	END IF;

	-- Lock the team row to avoid concurrent inserts/updates bypassing the limit.
	PERFORM 1
	FROM teams
	WHERE uid = NEW.team_id
	FOR UPDATE;

	SELECT COUNT(*)
	INTO member_count
	FROM users
	WHERE team_id = NEW.team_id;

	IF member_count >= 3 THEN
		RAISE EXCEPTION 'TEAM_MEMBER_LIMIT_EXCEEDED';
	END IF;

	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_enforce_team_member_limit ON users;

CREATE TRIGGER trg_enforce_team_member_limit
BEFORE INSERT OR UPDATE OF team_id ON users
FOR EACH ROW
WHEN (NEW.team_id IS NOT NULL)
EXECUTE FUNCTION enforce_team_member_limit();
