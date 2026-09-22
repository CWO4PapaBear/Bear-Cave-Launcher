# Account requests

The launcher preview includes a realm-aware Request an Account dialog with a preferred account name and Discord contact. Prepare Request generates text, Copy Request copies it, and Open Discord opens the owner's designated channel: https://discordapp.com/channels/1312920749866090628/1551338409358790877 . The user must paste and send the request themselves. No request is transmitted automatically or persisted. Closing clears the fields. This is an access request, not automatic registration. Channel visibility and posting permissions have not been verified; testers must have access.

Both realms currently use the owner-selected channel, with the requested realm included in the message. Do not assume they share accounts or an authentication database. GitHub remains the update host, not an account-request issue tracker. Automatic delivery would require a backend or bot; never embed a Discord webhook or bot token in the launcher.

A later HTTPS account service can validate requests, apply rate limits and support approved account provisioning. Keep database credentials and administrator commands on the server, never in the launcher. Approved users should set their password through a secure activation flow; do not collect passwords in requests or Discord messages. Destination, retention, duplicate handling and approval workflow remain undecided.
