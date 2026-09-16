# 06 · End-to-end control: when a rendered MP4 becomes a deliverable

The starter can generate assets and assemble them into an MP4. That output is a
**rendered candidate**. A production-ready deliverable needs a second layer that answers:

- Which exact source and shot plan governed this run?
- Which task attempt produced each candidate?
- Which exact take was approved for every required shot?
- Which hashes entered the edit, mix, grade, subtitles, and final encode?
- Which exact master did a person actually review?

This chapter explains that control layer. It does not add provider calls, spend money,
publish a video, or pretend that the current starter scripts automatically enforce it.

## One word called “done” hides several different facts

These events are not interchangeable:

1. A provider reports success.
2. The returned bytes are downloaded and technically readable.
3. A person accepts that exact take for its intended shot.
4. Every required shot has an accepted selection and the picture is locked.
5. The locked picture is mixed, graded, subtitled, encoded, and technically checked.
6. A person approves that exact delivery-master hash.

The first event proves only that a remote service finished a task. The last event is what
makes the file ready to deliver.

## The production graph

Use a small, explicit phase graph:

```text
source -> plan -> continuity -> generation_preflight -> generation -> selection
-> picture_lock -> finish -> final_qc -> delivery
```

Each arrow is a handoff of versioned artifacts, not permission for the next stage to fill
in missing upstream decisions. If the current shot plan does not define a gaze target,
the provider prompt should not quietly invent one. If a required motion take is rejected,
the edit should not silently replace it with a moving still.

## Four ledgers prevent false progress

Keep four kinds of state separate:

| Ledger | What it answers | Example |
|---|---|---|
| Entity state | Where is the video or shot in the workflow? | `selection / waiting_human` |
| Task attempt | What execution happened? | paid request 2, external task ID, cost |
| Artifact version | What exact bytes exist? | path, version, SHA-256, upstream hashes |
| Review verdict | Who decided what about which bytes? | human approval bound to one SHA-256 |

A provider task can be successful while its artifact is rejected. A file can decode
correctly while its performance is wrong. A previous approval does not apply to a new
encode.

## Build an artifact DAG

A directed acyclic graph (DAG) records which exact artifacts produced which descendants:

```text
approved source + shot plan + continuity pack
                  |
                  v
         provider request -> raw take -> review take -> selected take
                                                        |
                                                        v
                         native cut -> picture master -> grade/mix/subtitles
                                                        |
                                                        v
                                  final QC -> delivery master -> human verdict
```

Every node has a stable ID, version, path, SHA-256, owner, and state. Every edge says why
one node depends on another and binds both endpoint hashes. If an upstream node changes, all transitive descendants
become stale until rebuilt and reviewed.

Every reached phase also declares which artifact roles it requires. Passing gates for
that phase must collectively cover those roles; a green check over an unrelated file
cannot advance production, and every reached phase from planning onward needs a current
passing gate. The contract's canonical role floor cannot be removed; a run may only add
requirements, while audio/subtitle/continuity applicability comes from the receipt-bound
scope. Source snapshots, machine reports, human reviews, gates, and
authorizations use typed immutable evidence that repeats the exact IDs, hashes, verdicts,
scope, and decision time it claims to support.

This is stronger than checking whether a file exists. The current starter cache is keyed
mostly by spec and shot names, so a changed prompt or model does not always invalidate an
old file automatically.

## Provider success is candidate delivery

Use a lifecycle that preserves the distinction:

```text
planned -> authorized -> queued/running -> provider_succeeded
-> exact_bytes_downloaded -> integrity_checked
-> candidate_pending_human_review -> human_approved -> selected
```

If diagnostics actually find risks, record the optional
`integrity_checked -> diagnostics_flagged -> candidate_pending_human_review` branch;
do not label every successful task as defect-flagged.

Save the immutable input digest, provider/model revision, external task ID, cost, raw
output hash, and any review-transcode hash. If a submission response is ambiguous,
reconcile the original task before paying for another attempt.

Authorization evidence must self-bind the exact phase, shot and task IDs, provider/model,
cost/request caps, expiry, and whether it may resume a paused run. `audit_only` is always
read-only even if an older production authorization remains in the ledger.

Only a human-approved exact-hash review take can enter selection. A URL, thumbnail,
contact sheet, provider status, or technically valid MP4 cannot.

## Picture lock is exact frame arithmetic

At picture lock:

- every required shot or editorial unit appears exactly as declared;
- every clip points to the selected take ID and hash;
- source and timeline ranges use integer frames and half-open ranges;
- every source range stays inside the media's probed available range;
- clips are contiguous unless an explicit gap is part of the plan;
- the final end frame equals the intended runtime;
- frame-rate conversions, transitions, repeats, and holds are explicit.

[OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) is a useful
native interchange format for edit decisions. It represents timelines, tracks, clips,
gaps, transitions, media references, and source ranges. It does not contain the media
essence and does not prove that a source file exists, has enough transition handles, is
approved, or survived a lossy adapter round trip. Those checks remain separate.

See the official [serialized schema](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/otio-serialized-schema.md)
and [time-range model](https://opentimelineio.readthedocs.io/en/latest/tutorials/time-ranges.html).

## Finishing needs receipts

The finished image and sound are transformations, so record what actually happened.

### Color receipt

A color receipt should bind:

- the source-color claim or explicit assumption;
- configuration URI/version/hash and context;
- input and working spaces;
- ordered transforms and whether each was applied;
- display/view and whether it was baked;
- output primaries, transfer, matrix, range, and bit depth;
- exact input and output hashes.

“Warm,” “cinematic,” or “rich” describes creative intent, not a technical color path.
Correct metadata also does not prove that the grade looks good. OpenColorIO's official
[configuration guide](https://opencolorio.readthedocs.io/en/latest/guides/authoring/authoring.html)
and [display/view model](https://opencolorio.readthedocs.io/en/latest/guides/authoring/displays_views.html)
show why those facts must remain separate.

### Audio receipt

An audio receipt should bind:

- source stem hashes, sample format/rate, channel layout, and sample duration;
- processing tools/versions, ordered operations, and gain changes;
- the selected destination profile;
- loudness-meter standard/tool, integrated loudness, maximum short-term loudness, and
  maximum true peak;
- audiovisual sync result and exact output hash.

[ITU-R BS.1770](https://www.itu.int/rec/R-REC-BS.1770) defines measurement algorithms;
[EBU R 128](https://tech.ebu.ch/docs/r/r128.pdf) is one broadcast application of those
measurements. A broadcast target is not a universal target for every social platform.
Technical measurements do not replace human checks for intelligibility, emotion, music
balance, or impact.

### Subtitle and delivery receipts

Bind subtitle text to its source transcript, language, timebase, timing/coverage check,
safe-area/readability review, and sidecar-or-burned state. Bind the final encode to a
delivery profile that declares container, codec, frame geometry, pixel format, color
metadata, audio layout, and the selected measurement limits.

Changing subtitle text, font, placement, timing, crop, watermark, mix, grade, or encode
creates a new artifact. It is not the same approved master.

The graph must also prove the finish lineage: selected takes and the native cut feed the
assembly manifest; the approved edit blueprint feeds the native cut; the picture master
derives from that assembly; the picture/color blueprint feed the grade and color receipt;
the audio blueprint, stems, and locked timing feed the audio master/receipt; each subtitle
comes from its transcript/timebase and the native cut. The delivery master then binds the
graded picture, applicable sound/subtitles, delivery profile, and current receipts; final
QC binds both that exact master and profile.

State changes live in an append-only transition log. Forward events advance one phase
only after its gates cover required outputs; repair events move backward with an explicit
invalidation. The final event must equal the manifest's current state.

## The final human hash gate

The final reviewer should watch the exact delivery master—or a review proxy whose
transform and source hash are recorded—from start to finish at normal speed, intended
size, and with sound enabled when audio exists. The verdict records the reviewed master
SHA-256, review conditions, evidence, reviewer, and decision time.

Delivery requires both:

- a nonempty current machine gate binding the exact master and chosen delivery profile;
- every declared final gate present and passing; and
- a separate current human approval bound to those exact master bytes.

No filename, provider status, old proxy, previous encode, or aggregate video score can
substitute for that gate.

## What the starter enforces today

`scripts/make_short.py` generates or reuses assets, creates cards and subtitles, assembles
the timeline, mixes audio, applies a simple look, writes BT.709-tagged output, and probes a
few delivery fields. It currently does **not**:

- emit a content-addressed artifact DAG;
- maintain durable paid-task attempts and reconciliation;
- require approved selected-take hashes before assembly;
- author and validate a native OTIO cut;
- emit complete color, audio, subtitle, or delivery receipts;
- bind final QC and human approval to the output SHA-256.

The reusable control instructions live in
[`skills/video-run-control/SKILL.md`](../skills/video-run-control/SKILL.md), with the
detailed schema in its
[`run-manifest-contract.md`](../skills/video-run-control/references/run-manifest-contract.md).
Until the starter implements and tests those controls, use them as an explicit production
audit and call the generated MP4 a rendered candidate.

## Minimal delivery checklist

- Current source and plan hashes are known.
- Every paid task is authorized, costed, and reconcilable.
- Every required shot has one current exact-hash human-approved take.
- Picture lock uses exact take hashes and integer-frame ranges.
- Color, audio, subtitle, and delivery-profile receipts bind the current outputs.
- Final QC binds the exact delivery-master hash.
- A human approved those exact bytes under recorded viewing conditions.
- No upstream replacement or rejection left a descendant stale.

These controls are clean-room abstractions from established production ideas. For
versioned products and review separation, see [AYON publishing](https://docs.ayon.dev/docs/dev_publishing/)
and [Kitsu review workflow](https://kitsu.cg-wire.com/status-publish-review/). No
third-party workflow code is copied into this repository.
