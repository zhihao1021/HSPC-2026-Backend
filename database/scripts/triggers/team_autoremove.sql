CREATE OR REPLACE FUNCTION delete_empty_team_after_user_change()
RETURNS TRIGGER AS $$
BEGIN
	-- Only the previous team can become empty after delete/update.
	IF OLD.team_id IS NOT NULL THEN
		IF NOT EXISTS (
			SELECT 1
			FROM users
			WHERE team_id = OLD.team_id
		) THEN
			DELETE FROM teams
			WHERE uid = OLD.team_id;
		END IF;
	END IF;

	RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_delete_empty_team_after_user_change ON users;

CREATE TRIGGER trg_delete_empty_team_after_user_change
AFTER DELETE OR UPDATE OF team_id ON users
FOR EACH ROW
WHEN (OLD.team_id IS NOT NULL)
EXECUTE FUNCTION delete_empty_team_after_user_change();
