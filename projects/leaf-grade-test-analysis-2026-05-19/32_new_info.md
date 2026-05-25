select count(*) FROM saikyo_old.statements_mv where  empty(operation_name); -- 24,937,088
select count(*) FROM saikyo_old.statements_mv where  empty(contents_id);  -- 24,937,088

In the LEAF system we have 3 main applications: Bookroll (eBook reader), Moodle (LMS), and the Analysis app. Moodle/LMS and Analysis xAPI records do not have the Bookroll-specific `operation_name` and `contents_id` fields, so the approximately 25 million empty values come from Moodle/LMS and Analysis application records rather than missing Bookroll reading events.

Error on:

Candidate Bridge Query 1: Add Content Metadata:
- no `c.deleted_at` column in br_contents table
