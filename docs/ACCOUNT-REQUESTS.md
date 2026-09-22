# Account requests

The launcher preview includes a realm-aware Request an Account dialog with a preferred account name and Discord contact. Sending is disabled; nothing is stored or transmitted. Closing clears the fields. This is an access request, not automatic registration.

Recommended first deployment: a private request queue reviewed by the server administrator. Configure the destination independently for Main and PTR, without assuming they share accounts or an authentication database. The owner must choose the private destination before delivery is enabled. GitHub remains the update host, not a public account-request issue tracker.

A later HTTPS account service can validate requests, apply rate limits and support approved account provisioning. Keep database credentials and administrator commands on the server, never in the launcher. Approved users should set their password through a secure activation flow; do not collect passwords in requests or Discord messages. Destination, retention, duplicate handling and approval workflow remain undecided.
