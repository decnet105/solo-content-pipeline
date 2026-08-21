---
name: social-post
description: >
  Discipline for writing social main-posts (Reddit-style forums, image-and-text feeds,
  microblogs) that read as a real person, not as AI. Use this when drafting a top-level
  post, a photo/text post, or a longer piece. Two things do the work: a de-AI blacklist of
  universal "tells" to delete on sight, and platform reality — forums are hostile to
  self-promotion, so lead with a zero-product value post and only reveal the product when
  someone asks in comments; scan for automod trigger words before posting; pick a genuine
  life/discussion flair, not tech/ad. Draft replies to other people's comments with the
  companion skill `social-reply`.
---

# Social main-posts

Use this for **top-level posts**. Draft **replies to others' comments** with `social-reply`
(it shares the same de-AI blacklist).

## Before every post

1. Run the **de-AI blacklist** (below). After writing, read each sentence and ask: does
   this sound like a school essay or an LLM? If yes, cut it.
2. Prefer understated, specific, human, slightly "leaky" text — a little imperfect reads
   as real; a flawless, over-polished post reads as generated.
3. Match the platform's length and register (short and lowercase-friendly on a microblog;
   a punchy hooked title plus a conversational body on an image/text feed; a plain,
   member-like tone on a forum).
4. **Generate the actual copy with a strong writing model** — this is a writing task, and
   a capable model with these constraints beats a quick one-liner.

## The de-AI blacklist (delete on sight — shared with `social-reply`)

These patterns are the strongest "this was written by AI" tells. Any one of them present =
rewrite.

- **Fake sensory intensity standing in for being moved.** "My scalp went numb," "goosebumps
  all over," "chills down my spine," "my eyes welled up," "my heart skipped." Using a body
  reaction to fake impact is the single heaviest AI move. Give a real, specific observation
  or a real detail instead of pretending to be physically struck. (Generic idiom example to
  avoid, labeled: 头皮发麻 / "scalp went numb.")
- **Forced parallelism and antithesis.** Tidy matched clauses and neat "not X but Y"
  closers ("no matter how expensive X is, it can't buy Y"). Real people don't talk in
  balanced couplets.
- **Summarizing-emotion sentences.** "It just pulled me right back," "at the end of the
  day," "what we really miss is…". Don't narrate the feeling; show the thing.
- **Inspirational / conclusion-y closers.** A pretty moral, an uplifting aphorism, a
  wrapped-in-a-bow final line. Stop when the point is made.
- **Stiff written connectives piled up.** "Thus," "therefore," "for this very reason,"
  "as such." Speech doesn't stack these.
- **Immersive first-person openers.** "I read it in one breath," "finished it in one
  sitting," "it left me…". Open on a real detail or a concrete fact instead.
- **English AI-tells** (if writing in English): "This resonates (so deeply)," "Couldn't
  agree more," "So beautifully said," "Thank you for sharing this," "As someone who…, I…,"
  "This hit different," "There's something about…," em-dash pileups, "Not only… but also…."

What to write instead: one concrete detail or data point, plain everyday words, a modest
open ending that doesn't say everything or moralize. Specific beats abstract every time.

## Platform reality: forums are hostile to self-promotion

Community forums (Reddit-style subs and similar) are **not an ad channel**. They are a
"be a real member for a while and the thing you made gets mentioned on its own" channel.
Hard lessons:

1. **Self-promotion is near-zero-tolerance.** However clean, restrained, link-free, and
   openly "I'm the person who made this," the moment a post *names your product / app /
   store listing*, a mod or automod may remove it. So lead with a **zero-product value
   post**: strip every brand / product / store / platform / link / feature bullet, and
   leave only a genuine story + one real insight + one real question. The post must stand
   on its own as an honest, good post even if nobody ever asks about a product. Reveal the
   product **only when someone asks in the comments** (see the reveal-when-asked pattern in
   `social-reply`).
2. **Watch the automod keyword filters.** Many communities auto-remove posts that contain
   certain service names or spam-adjacent terms (things like "scan QR code," "register /
   add me," "sign up," specific messaging-service names, and their historical aliases). A
   single innocent nostalgic mention can trip the filter. **Scan your draft word by word
   for trigger terms before posting** and swap them for neutral anchors. If your post *is*
   removed, it's often the keyword filter, not a promotion judgment — check the actual
   removal reason before concluding anything, and consider a polite modmail so the removal
   isn't counted against you.
3. **Pick the right flair.** Choose a genuine "life / discussion / personal story" flair.
   Do **not** pick "tech / promo / ad" — that flags your post for scrutiny as an ad on
   sight.
4. After posting, work the comments in a real human voice for the first couple of hours,
   and don't cross-post the same thing everywhere immediately.

## Watch for trigger words (checklist)

Before you hit post, grep your own draft for:

- Product / brand / app / store names, and any download or install language.
- Links of any kind.
- Messaging-service names and their old aliases; "scan," "QR," "register," "sign up,"
  "add me / add friend."
- Feature bullet lists that read like a spec sheet.

If any appear and the venue is a self-promotion-hostile forum, cut them and move the
reveal to the comments.

## Publishing discipline

Posting to an external platform is irreversible. Have a human review anything before it
goes out. Attach images and video produced by your other pipelines; keep this skill scoped
to the words.
