CREATE OR REPLACE FUNCTION update_user_verify_state()
RETURNS TRIGGER AS $$
BEGIN
    -- 當 image_front 或 image_back 更新時，同步更新對應 user 的 verify_state 和 student_verified
    UPDATE users
    SET verify_state = 1, student_verified = FALSE
    WHERE uid = NEW.user_uid;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER sid_image_update_verify
AFTER UPDATE ON sid_image
FOR EACH ROW
EXECUTE FUNCTION update_user_verify_state();