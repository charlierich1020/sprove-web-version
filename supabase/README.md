# supabase/

Where the deployed Edge Functions belong.

Two functions are live on the project and answering requests — `ai-gateway`
(401 to an unauthenticated call) and `stripe-webhook` (400 to an unsigned one) —
but their source is not here. It exists only in the Supabase dashboard, which
means the code that moves money cannot be reviewed in a pull request, has no
history, and cannot be rolled back.

Pull it down (needs a Supabase personal access token, so the owner runs it):

    npx supabase login
    npx supabase link --project-ref tseszaprvtvqrkfpditu
    npx supabase functions download ai-gateway
    npx supabase functions download stripe-webhook

Read `stripe-webhook` before committing: it must verify the Stripe signature
against the RAW request body via `stripe.webhooks.constructEvent`. A webhook that
trusts an unsigned POST lets anyone mark a booking paid.

Check for hardcoded keys in what arrives. Secrets belong in Edge Function
secrets, never in a file here — see SUPABASE-OWNERSHIP.md.

Full findings: docs/backend-audit-2026-08-13.md
