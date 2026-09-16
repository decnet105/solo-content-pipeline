---
name: video-run-control
description: >
  Track and validate one complete AI video run from an approved source and shot
  plan through provider candidates, selected takes, picture lock, sound/color/
  subtitle finishing, exact-hash master review, and delivery. Use for end-to-end
  production state, cross-stage handoffs, stale-dependency repair, resuming a run,
  or deciding whether a rendered video is actually ready to deliver. Do not use
  it to write content, call a provider, spend money, publish, or grant human approval.
---

# End-to-end AI video run control

Use this skill as the control plane for one video run. It links exact versions and
review evidence across the pipeline; it does not replace the tools or people that
create the source, shots, continuity assets, generated takes, edit, mix, grade, or
subtitles.

## Resolve current truth first

Identify the current approved source or brief, current shot plan, current human
decisions, and any pause or spending boundary. Record each governing file by path and
SHA-256, then bind the ordered roots and resolved states in a typed immutable source-
snapshot receipt. A filename such as `final`, an old approval, a provider URL, or a
completed render does not override newer evidence.

If the source is ambiguous, a required approval is absent, or production is not
authorized, keep the run in `audit_only`. Analysis and local validation may continue;
provider calls, paid retries, delivery, and publication remain blocked.

## Keep four ledgers separate

- **Entity state**: the readiness of the video, sequence, shot, and production stage.
- **Task attempt**: one bounded execution, including input digest, external task ID,
  cost, retry class, and outcome.
- **Artifact version**: immutable path, version, SHA-256, upstream hash bindings, and
  technical/publication state.
- **Review verdict**: machine or human decision bound to exact artifact bytes and
  evidence.

Do not collapse these into one `status`. A provider task may succeed while its returned
file is only a candidate. A file may pass technical checks and still fail story,
continuity, motion, sound, or taste review.

## Run an artifact graph, not a mutable folder chain

Use this generic phase order:

```text
source -> plan -> continuity -> generation_preflight -> generation -> selection
-> picture_lock -> finish -> final_qc -> delivery
```

Read [the run manifest contract](references/run-manifest-contract.md) before creating,
auditing, resuming, repairing, or delivering a run.

1. Register every consumed or produced file as an immutable artifact version. Bind every
   derivative and both ends of every dependency edge to the current exact hashes.
2. Start a phase only when all required predecessors and gates are current. Declare the
   required artifact roles for every reached phase; the contract's canonical floor may
   only be extended, never reduced. Collectively, its passing gates must cover all of
   them, so an unrelated report cannot satisfy the phase. Return a missing field to its
   named owner instead of inventing it downstream.
3. Treat every paid submission as a separate authorized task attempt. Back each
   authorization with typed immutable evidence that self-binds its phase, shots, task IDs,
   provider/model, cost/request caps, expiry, and resume semantics. An uncertain
   submission becomes `reconciliation_required`; it never licenses a blind resubmit.
4. Treat provider completion as candidate delivery only. Download and hash the exact
   bytes, create and bind any review proxy separately, probe the media, and obtain a
   current human verdict before selection. Machine reports, human review events, and
   phase-gate evidence must be typed immutable JSON that repeats the reviewed artifact
   ID/SHA and verdict; old evidence cannot be relabeled onto new bytes.
5. Select one exact-hash approved take for every required shot or edit unit. A missing,
   rejected, stale, or silently substituted shot blocks picture lock.
6. Express picture lock in integer frames. Prefer native OpenTimelineIO (`.otio`) for
   edit decisions when supported, and separately prove that all media references, source
   ranges, handles, frame rates, and selected hashes are valid.
7. Finish only from the locked picture and approved blueprints. Record separate color,
   audio, subtitle, delivery-profile, and final-QC artifacts rather than hiding those
   transformations inside a filename.
8. Bind the final human delivery verdict to the exact delivery-master SHA-256 and its
   review conditions. Require a separate nonempty machine gate over that master and its
   delivery profile; an empty gate list is not success. Any re-encode, crop, mix,
   subtitle, watermark, or color transform creates new bytes and invalidates the old
   verdict.
9. When an upstream artifact changes, mark every transitive descendant stale and route
   `next_action` to the earliest affected owner.

## Distinguish receipts from taste

- An OTIO timeline or assembly manifest proves edit decisions and arithmetic, not that
  referenced media exists, is approved, or looks good.
- A color receipt proves the declared source assumption, configuration, transforms,
  display/view, and output metadata; it does not prove a pleasing grade.
- An audio receipt proves the declared sources, processing, delivery profile, loudness,
  true peak, and sync checks; it does not prove intelligibility, emotion, or musical
  impact.
- Automated video metrics may flag risky frames or timecodes; they do not grant artistic
  approval.

The final review must watch the exact bound master or a cryptographically bound proxy at
normal speed, intended size, with sound enabled when the video contains audio.

## Current starter boundary

The bundled `make_short.py` assembles a rendered candidate. It does not emit or validate
the manifest contract, content-address its cache, enforce selected-take gates, author a
native OTIO cut, measure a delivery audio profile, produce a complete color receipt, or
grant a final human verdict. Do not describe these controls as automated until code and
tests actually enforce them.

## Stop conditions

Stop before external mutation when authorization is missing, expired, or narrower than
the request; a paid task is unresolved; a dependency hash is stale; or a predecessor gate
is incomplete. `audit_only` always forces external mutation off, even if an older
authorization record still exists. Stop before picture lock if any required shot lacks
an exact-hash approved take. Stop before delivery if the timeline, finish receipts,
final-QC evidence, or current human verdict for the exact delivery master is missing.
