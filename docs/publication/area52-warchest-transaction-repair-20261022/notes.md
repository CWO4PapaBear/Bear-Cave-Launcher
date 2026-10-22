# Area 52 Warchest login crash correction

Corrects a server crash during the first account Warchest delivery at login. The gift's item and mail statements now execute on the appropriate asynchronous database connection, with transaction success checked before exposing the mail.

The six Warchest rewards, four non-Unique 22-slot satchels, vanity entry and once-per-account eligibility are unchanged. Existing delivery receipts remain intact. No character reset or replacement item is required; log in after recovery to receive the gift if your account has not received it.

Engineering checks include the original connection-type failure, repaired native function, failure and duplicate-account paths, and stopped-server recovery rollback. In-game acceptance remains pending. Area52 distribution stays outside the future upstream reward PR. No verification/certification labels changed.
