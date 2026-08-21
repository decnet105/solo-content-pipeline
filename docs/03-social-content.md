# 03 · Social Content

Making the video is half the job. The other half is writing the words around it — the post that carries it, and the replies you leave under other people's posts. This repo ships two "skills" for exactly that:

- `skills/social-post/SKILL.md` — writing a main post.
- `skills/social-reply/SKILL.md` — writing a comment or reply in a community.

A **skill** here is just a plain-text instruction file that teaches your coding agent your standards, so it drafts in your voice instead of generic AI voice. You point the agent at the skill and say "draft a post about X" or "write a reply to this comment," and it follows the rules. The two below encode the lessons that actually matter.

---

## Killing the AI "tell"

Readers can smell AI-written text, and the moment they do, they stop trusting it. Both skills are built around removing that tell. The patterns to strip out:

- **Throat-clearing intros.** "In today's fast-paced world…", "Let's dive in!", "Have you ever wondered…". Start with the actual thing.
- **The rule-of-three cadence.** Real people don't naturally list "engaging, informative, and delightful" every sentence. Vary your rhythm.
- **Hype adjectives.** "game-changing," "revolutionary," "seamless," "powerful." Cut them or replace with something concrete.
- **The tidy bow.** "At the end of the day," "The bottom line is," a summarizing final sentence that restates everything. Just stop when you're done.
- **Over-hedging and over-explaining.** Say the thing once, plainly.
- **Perfect punctuation polish.** Em-dashes everywhere, flawless parallel structure, zero fragments. Humans write looser. A short fragment is fine.
- **Emoji garnish and section headers** in places a person would never use them.

The test in both skills: read it out loud. If it sounds like a person talking to a person, ship it. If it sounds like a brochure, rewrite it.

---

## The platform reality (this is the part people get wrong)

Communities — forums, subreddits, group chats — are not billboards. They are hostile to advertising by design and by culture. If you show up to promote your thing, you will be downvoted, removed, or banned, and you'll have burned the account. The skills bake in the following hard-won rules.

### Give value with zero product in it

Your posts should be genuinely useful or interesting **on their own**, with no mention of what you're building. Share a thing you learned, a result, a mistake, a useful comparison. The value stands alone. If someone finds it good, _they_ ask what you used or what you're working on — and only then, in a reply, do you mention your project, briefly and without a hard sell. "Reveal when asked," never "lead with the pitch."

This feels backwards if you're in a hurry to grow. It's the only thing that works long-term in real communities. A hundred people who trust you beat a thousand who flagged you as a spammer.

### Watch the automod keyword traps

Most large communities run an automated moderator that silently removes posts containing certain triggers — link shorteners, the word "promo," store URLs, referral-looking links, sometimes brand names or "DM me." Your post can vanish without a visible error and you'll never know why. Before posting:

- Read the community's rules and its automod/sticky posts.
- Avoid obvious trigger words and drop naked links, especially store or download links.
- If you must reference something, describe it in words and let people ask, rather than pasting a URL.

The `social-post` skill keeps a running list of these traps; add to it every time you find a new one.

### Pick the right flair / tag

Many communities require a **flair** (a category tag) on every post and auto-remove untagged ones. Posting a "Show / I made this" flair on a discussion sub, or the wrong topic tag, gets you removed regardless of content quality. Match the flair to both the community's taxonomy and your post's actual intent. When in doubt, the "discussion" or "question" flair is safer than a "promotion" one.

### Match the room

Every community has its own tone, in-jokes, and pet peeves. A reply that lands in one room reads as tone-deaf in another. The `social-reply` skill is specifically about sounding like a regular who already belongs there: short, on-topic, no hooks, no links, no funneling toward your thing. Just a real person adding a real thought.

---

## How to use the skills

With your coding agent open in this repo:

1. Point it at the skill: _"Follow `skills/social-post/SKILL.md`. Draft a post for a hobby-photography community about how I sped up my editing workflow — value only, no mention of any product."_
2. Read the draft out loud. Push back on anything that sounds like AI or like an ad.
3. For replies: paste the comment you're responding to and say _"Follow `skills/social-reply/SKILL.md` and write a short, human reply — no links, no pitch."_
4. **Every time a real reader (or a mod) reacts badly and you learn something,** have the agent append that lesson to the skill file. The skills get sharper the more you use them, and they never forget a lesson twice. That feedback loop is the whole method, and it's the subject of the next doc.

Next: [docs/04 · How this was built](04-how-this-was-built.md).
