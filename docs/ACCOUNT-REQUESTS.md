# Account requests

The launcher has a Request an Account button opening a realm-aware form with a preferred account name and email or Discord username. Send Request is disabled until the backend is configured. Nothing is stored or transmitted; closing clears the fields. The copy-and-post workflow has been removed. Applicants will not need membership in the Discord server.

Planned flow: launcher form → private HTTPS request service → Discord webhook → administrator approval. The service will validate input, limit spam, prevent Discord mentions and return a request reference only after accepting the request. Database credentials and the webhook URL belong exclusively on the server, never in the launcher, manifests or repository.

Webhook destination, hosting, retention, duplicate handling and approval workflow will be configured later. Do not assume Main and PTR share accounts or an authentication database. Do not collect passwords in requests; arrange secure password setup after approval. No webhook URL has been stored or tested and no messages have been sent.
