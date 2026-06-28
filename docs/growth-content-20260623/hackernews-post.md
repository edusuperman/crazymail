Show HN: TempMails – Disposable email for sign-up verification, no signup required

I built tempmails.top because I got tired of services demanding real email addresses just to read a forum post or download a PDF.

How it works:

When you visit the site, we generate a random mailbox on one of our rotating domains. You get an instant inbox view that polls for new messages via short-polling (2s intervals). Emails arrive and display in real-time without any account creation or personal data.

Technical stack:
- Cloudflare Workers for the edge API layer, keeps latency under 50ms for most requests
- Mail received via Postfix on a $5 VPS, piped through a custom handler that parses MIME and stores messages in SQLite
- Each mailbox auto-deletes after 24 hours via a cron job that wipes both the SQLite rows and the Postfix mailbox files
- Frontend is vanilla JS, no framework, total page weight 12KB gzipped

Privacy guarantees:
- Zero cookies, zero analytics scripts, zero localStorage on the main page
- No IP logging on the mail server side
- We don't track which services you're verifying against
- All data is ephemeral by design – 24-hour TTL, no backups, no replicas

Performance:
- Mail delivery typically under 5 seconds from sender to inbox display
- Tested with Gmail, Outlook, and ProtonMail senders
- Handles ~200 concurrent inboxes before the VPS needs scaling

Limitations I should be upfront about:
- Some services (banks, government portals) block disposable email domains – this is a cat-and-mouse game and we lose sometimes
- Attachments over 1MB are dropped to keep storage costs sane
- No guarantees on domain reputation staying high; some email providers may start deferring our mail
- Short-polling isn't ideal but WebSockets felt like overkill for a 24-hour TTL service

Domain rotation happens monthly to stay ahead of blocklists. Currently running 6 domains with MX records pointed at the same Postfix instance.

The whole thing runs for about $15/month. Built this as a utility I personally needed. Feedback on architecture or security holes welcome.