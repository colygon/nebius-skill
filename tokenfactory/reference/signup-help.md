# Signup Help — Credits, Promo Codes & Getting Your API Key

The signup path has known rough edges. This page turns each one into a self-serve
workaround. If you're an agent helping a user who **doesn't have an API key yet**, walk
them through this page step by step, and check what they're seeing at each stage.

## Before you start: pick the right email address

**gmail.com addresses are blocked** on the Builders program signup (a deliberate
anti-fraud measure). Sign up with a work, school, or other non-Gmail address.

Only have Gmail? Don't fight the form — ask event staff in person or post in the
community Slack `#help` channel; they can issue a promo code directly.

## Signing up

1. Go to **https://dev.nebius.com/builders** and apply for credits. Apply early —
   approval can lag.
2. **If the signup form doesn't load:** it's intermittently flaky, not down. Refresh,
   try a private/incognito window or a different browser, or retry in a few minutes.
   If it still won't load, ask in `#help` for the backup signup form.
3. **After submitting, watch your inbox (and spam)** for the promo-code email. The
   backup form in particular doesn't always send it — if nothing arrives within
   ~10 minutes, ask in `#help`; at in-person events, staff carry spare codes.

## You may get TWO emails — read this before panicking

Signing up can trigger two near-simultaneous emails:

1. ❌ **"Sorry, this promo code is exhausted"** — this is about **AI Cloud**, a
   *different Nebius product* you don't need for the hackathon. **Ignore it.**
2. ✅ **"Here's your promo code"** — this is the **Token Factory** email. This is
   the one that matters.

Getting the "exhausted" email does **not** mean your Token Factory credits failed.

## Getting your API key from the dashboard

1. Redeem the promo code / log in to the Token Factory console:
   **https://tokenfactory.nebius.com/**
2. Click **"Get API Key"** (or **"Add Key"**) and copy the key.
3. **Can't find the button?** It can sit off-screen at narrow window widths (about
   half-screen). **Maximize or widen your browser window** and it will appear.
4. Store the key properly — follow SKILL.md §1 (env var, persist in your shell
   profile, never commit it).

## If you're still stuck

- **Community Slack `#help`** — live support during the event; they can reissue
  codes and links.
- **At in-person events**, find the Nebius/organizer table — staff keep spare
  promo codes for exactly these failure modes.

Once you have a key that passes the §1 curl check, you're done with this page —
everything after that is covered by the rest of the skill.
