# Generic video run manifest contract

Schema version: `1.0`

## Purpose

A run manifest is the audit and routing record for one video production run. It links
approved source truth to selected takes, picture lock, finishing, final QC, and delivery
without copying the creative content owned by those stages. It is not a screenplay,
provider payload, edit file, approval note, or QC report.

Keep old manifests as history. When the governing source or another material dependency
changes, create a superseding manifest that points to the prior manifest's exact hash.
Do not edit history into agreement.

`previous_manifest_ref` is either null or `{path,sha256}` pointing to immutable JSON with
a different `run_id`. It is historical lineage, not permission to inherit prior gates or
authorization.

Paths are repository-relative, contain no `..`, and bind 64-character lowercase SHA-256
values. Times are timezone-aware ISO 8601. Timeline arithmetic uses integer frames and
half-open ranges.

## Required top-level records

```text
schema_version, run_id, project_id, video_id, mode, created_at, updated_at,
source_snapshot, state, scope, artifacts, dependency_edges, phase_requirements, gates,
authorizations, cost_state, task_attempts, shot_progress, handoffs, timeline,
finish, invalidations, transition_log, previous_manifest_ref, next_action
```

`mode` is `audit_only`, `candidate_run`, `authorized_production`, or
`delivery_review`. The phase order is:

```text
source -> plan -> continuity -> generation_preflight -> generation -> selection
-> picture_lock -> finish -> final_qc -> delivery
```

Allowed run states are `blocked`, `ready`, `in_progress`, `machine_pass`,
`waiting_human`, `human_approved`, `rejected`, and `superseded`. Authorization remains
orthogonal to phase and state; changing a state string cannot authorize spending or
publication.

`state` is:

```text
phase, run_status, entered_at, blocker_ids[]
```

The phase and status use the canonical values above, `entered_at` is timezone-aware, and
blocker IDs are unique. The last transition event must reproduce the exact current
`phase` and `run_status`.

## Source snapshot and scope

`source_snapshot` identifies the exact source/brief, creative plan, and current authority
record that govern the run. Each reference resolves to a registered artifact and hash.
Record the newest relevant human verdicts separately from the files they review.

It also contains `evidence_ref={path,sha256}` to typed immutable JSON with:

```text
evidence_type=source_snapshot, snapshot_id, recorded_at,
root_bindings[]={artifact_id, role, sha256},
production_track_status, newest_human_verdict_artifact_ids[], scope, phase_requirements
```

`production_track_status` is `PAUSED`, `CANDIDATE_AUTHORIZED`, or
`PRODUCTION_AUTHORIZED`. The receipt repeats the exact `scope` and `phase_requirements`
objects as well as the ordered roots and resolved state. Changing a root hash, state,
scope, or project-specific requirement requires a new receipt; editing only manifest
fields cannot redefine current truth. A decided snapshot without locally verifiable
receipt bytes fails closed.

`scope` defines:

```text
required_shot_ids, target_runtime_frames, fps_num, fps_den,
width, height, aspect_ratio, audio_expected, subtitle_languages,
required_continuity_roles
```

Every required editorial unit has a unique ID. Title cards, gaps, inserts, repeated units,
and intentional holds must be explicit; do not create untracked filler to make the
runtime work. `required_continuity_roles` is a unique list of project-specific continuity
artifacts in addition to the canonical `continuity_pack`; because the source receipt
repeats `scope`, it cannot be silently reduced later. `audio_expected=true` makes the
audio blueprint/master/receipt mandatory. Every listed subtitle language makes its
transcript/timebase and subtitle master mandatory.

## Immutable artifact versions

Each artifact contains at least:

```text
artifact_id, role, owner, path, sha256, version, representation_role,
byte_size, mime_type, technical_state, authority_state, publication_state,
machine_validation, human_review, supersedes
```

Keep these meanings separate:

- `technical_state`: whether bytes are queued, processing, ready, broken, or missing.
- `publication_state`: candidate, published-for-controlled-use, approved, rejected,
  stale, superseded, or archived.
- `authority_state`: candidate, human-approved, or revoked; it does not follow from file
  readiness or provider completion.
- `machine_validation`: a verdict bound to the artifact SHA and an exact report.
- `human_review`: a verdict bound to the artifact SHA and exact review evidence.

`published-for-controlled-use` means addressable by stable path and hash. It does not mean
creatively approved or safe to deliver.

Common generic roles include:

```text
source_truth, creative_plan, shot_contract, edit_blueprint, audio_blueprint,
color_blueprint, continuity_pack, generation_plan, provider_request_state,
raw_take, review_take, selection_manifest, native_otio_cut,
assembly_manifest, picture_master, graded_picture_mezzanine,
color_receipt, audio_stem, audio_master, audio_receipt,
transcript_timebase, subtitle_master,
delivery_profile, final_qc_report, delivery_master, delivery_verdict
```

A review proxy is its own artifact. Its record must bind the source hash and the complete
transform used to make the proxy. A thumbnail, contact sheet, URL, or mutable `latest`
alias cannot stand in for production identity.

## Dependency graph and handoffs

Each dependency edge records `from_artifact_id`, `from_sha256`, `to_artifact_id`,
`to_sha256`, `relation`, and `required`. IDs and hashes must resolve to the current exact
nodes; self-edges and cycles are forbidden. Common relations are
`derived_from`, `validated_by`, `reviewed_by`, `compiled_from`, `selected_from`,
`assembled_from`, and `delivered_from`.

Every consumer binds the current upstream hashes in its evidence. Each handoff records:

```text
handoff_id, from_owner, to_owner, artifact_bindings, status, change_request_ref
```

An accepted handoff binds exact current hashes. If a required field is missing, return a
keyed change request to its owner; do not repair source, continuity, motion, edit, or sound
truth inside a downstream prompt or manifest.

## Gates and reviews

A gate contains:

```text
gate_id, required_for_phase, kind, verdict, artifact_bindings,
evidence_ref, reviewer, reviewed_at
```

Machine gates pass only as `machine_pass`; human gates pass only as `human_approved`.
Every decided gate binds one or more `{artifact_id, sha256}` pairs and exact evidence. A
later rejection or revocation for the same bytes wins over an older pass and invalidates
descendants.

`phase_requirements` maps each phase to `required_roles[]` and
`required_artifact_ids[]`. It may add project-specific requirements but may not remove
the canonical floor below. Collectively, current passing gates for that same phase must
cover every declared requirement and every floor item:

```text
plan                 every source_truth root, creative_plan, every required shot_contract,
                     edit_blueprint,
                     color_blueprint; audio_blueprint when audio_expected
continuity           continuity_pack plus every role in scope.required_continuity_roles
generation_preflight generation_plan
generation           provider_request_state plus every returned raw_take
selection            selection_manifest plus every selected review_take exact ID
picture_lock         native_otio_cut, assembly_manifest, picture_master
finish               graded_picture_mezzanine, color_receipt, delivery_profile;
                     audio_master/audio_receipt when audio_expected;
                     transcript_timebase + subtitle_master for every subtitle language
final_qc             final_qc_report, delivery_master
delivery             delivery_profile, final_qc_report, delivery_master
```

An unrelated resolver, thumbnail, or old report cannot satisfy a phase merely because it
has a passing verdict. From `plan` onward, every reached phase needs at least one current
passing gate; deleting all gates is a failure, not an empty success.

Every evidence reference is exactly `{path,sha256}`. Machine report JSON contains:

```text
evidence_type=machine_validation, evidence_id,
subject_artifact_id, subject_sha256, verdict,
validator_id, validator_version, decided_at
```

Human review-event JSON contains:

```text
evidence_type=human_review, review_event_id,
subject_artifact_id, subject_sha256, verdict,
reviewer, authority_role, decided_at, supersedes_review_event_id
```

Gate JSON contains:

```text
evidence_type=gate, gate_id, kind, verdict,
artifact_bindings[]={artifact_id,sha256}, reviewer, reviewed_at
```

Every field repeats the manifest value exactly. Review events for motion takes and
delivery masters additionally repeat every viewing-context field below, including
`review_proxy_artifact_id`. A manifest-authored status without locally hash-verifiable
evidence bytes is not a pass.

For a motion take or delivery master, human review also records:

```text
subject_sha256, review_proxy_artifact_id, review_proxy_sha256, review_proxy_of_sha256,
timeline_context_sha256, color_receipt_sha256, audio_master_sha256,
display, view, view_baked, playback_speed, audio_enabled, decided_at,
supersedes_review_event_id
```

Use `playback_speed=1.0` for the acceptance pass. Frame stepping and slow motion may
diagnose a defect after normal-speed viewing; they do not replace it.

## Authorization, cost, and task attempts

Authorization records exact allowed task IDs, shot IDs, provider/model, expiry, maximum
cost, and maximum paid requests. There is no implicit authorization. Diagnostics do not
silently become production permission.

Every authorization has `evidence_ref={path,sha256}` to immutable typed JSON containing:

```text
evidence_type=authorization, authorization_event_id,
authorization_id, kind, status, allowed_phase,
allowed_shot_ids[], allowed_task_ids[], provider, model,
currency, max_cost, max_paid_requests,
does_not_resume_paused_run, expires_at
```

Every value repeats the manifest exactly. Any scope, currency, cap, expiry, provider, or
resume change requires new evidence; reusing an old receipt while widening manifest
fields is invalid.

Keep `currency`, `authorized_cap`, `reserved`, `actual`, and `paid_request_count` in a
separate cost ledger. Authorization, task, and ledger currencies must match. Reserved and
actual cost may not exceed the current authorization.

Each task attempt records:

```text
task_id, phase, shot_id, attempt_no, paid, status, provider, model,
idempotency_key, immutable_input_digest, input_bindings, output_artifact_ids,
external_task_id, authorization_id, cost_currency, estimated_cost, actual_cost,
resubmit_allowed, prior_task_id
```

Recommended provider-task states are:

```text
planned -> authorized -> queued/running -> provider_succeeded
-> exact_bytes_downloaded -> integrity_checked
-> candidate_pending_human_review -> human_approved -> selected
```

`provider_succeeded` describes the service lifecycle only. It cannot select a take or
advance the production. An uncertain submission becomes `reconciliation_required` with
`resubmit_allowed=false`; polling and downloading are not new paid attempts.
If diagnostics find risks, insert the optional branch
`integrity_checked -> diagnostics_flagged -> candidate_pending_human_review`; the state
means flags exist, not that every successful task is defective.

## Required shots and selection

Every required shot has one progress record:

```text
shot_id, generation_plan_artifact_id, task_ids,
returned_take_artifact_ids, selected_take_artifact_id,
selection_gate_id, assembly_clip_id, qc_gate_ids
```

The selected take must be a reviewable media artifact with current machine validation and
current human approval bound to its exact SHA. A raw take, provider status, URL, contact
sheet, technically valid file, or old approval is not eligible.

## Picture lock and OTIO

At picture lock, timeline clips begin at frame zero, are contiguous and non-overlapping,
and end at `target_runtime_frames`. Each required edit unit appears exactly as declared.
A clip records:

```text
clip_id, shot_id, take_artifact_id, take_sha256,
available_start_frame, available_end_frame,
source_in_frame, source_out_frame, timeline_in_frame, timeline_out_frame
```

Ranges are half-open; source and timeline duration must match. Timeline frame rate must
match scope. Each source range must remain inside the media's probed available range.
Each take hash must equal the current selected artifact for that shot.

Prefer native OpenTimelineIO (`.otio`) as the edit-decision artifact when supported.
Adapter formats are derivatives and require a feature-loss/round-trip record. Before
assembly, separately probe the real media and reject missing references, out-of-range
source windows, insufficient transition handles, unsupported effects or nesting, and
mixed rates without an explicit conversion. OTIO carries edit decisions, not media
essence or approval.

## Finishing receipts

`finish` contains:

```text
selection_manifest_artifact_id, native_timeline_artifact_id,
assembly_manifest_artifact_id, picture_master_artifact_id,
graded_picture_artifact_id, color_receipt_artifact_id,
audio_master_artifact_id, audio_receipt_artifact_id,
subtitle_master_bindings[]={language, transcript_timebase_artifact_id,
subtitle_master_artifact_id}, delivery_profile_artifact_id,
final_qc_report_artifact_id, delivery_master_artifact_id,
required_final_gate_ids[], human_delivery_gate_id, delivery_status
```

`delivery_status` is `not_started`, `candidate`, `machine_pass`, `waiting_human`,
`human_approved`, `rejected`, `stale`, or `delivered`. Conditional fields may be null or
empty only when the receipt-bound `scope` says that component is not applicable.

Phase/status completeness is fail-closed:

- before `picture_lock`, unfinished downstream artifact IDs may be null;
- at `picture_lock` or later, selection manifest, native timeline, assembly manifest, and
  picture master are non-null;
- at `finish` or later, graded picture, color receipt, delivery profile, and every
  scope-required audio/subtitle binding are non-null;
- at `final_qc` or later, final-QC report and delivery master are non-null;
- `machine_pass` or later requires nonempty `required_final_gate_ids`; and
- `human_approved` or `delivered` requires `human_delivery_gate_id`.

Required exact-hash graph edges make the finish reproducible:

- the assembly manifest depends on the selection manifest, native timeline, and every
  selected take used by the cut;
- the picture master derives from that assembly manifest;
- the native timeline derives from the approved edit blueprint;
- the graded picture derives from the picture master and approved color blueprint, while
  the color receipt binds those inputs and the graded result;
- when audio is expected, the audio master derives from the approved audio blueprint,
  every used audio stem, and native-timeline/picture-lock timing; the audio receipt binds
  those inputs, the output, and delivery profile;
- for every subtitle language, the subtitle master derives from its transcript/timebase
  and the native timeline;
- the delivery master derives from the graded picture, applicable audio/subtitle
  masters, and delivery profile, and is validated by the current color/audio receipts;
- the final-QC report binds both the delivery master and delivery profile.

Missing one of these edges is missing lineage even if every file exists. A receipt must
bind the current artifact SHA; an old receipt cannot validate a rebuilt master.

### Color receipt

Record at least:

- source-color claim and supporting evidence or explicit assumption;
- fixed configuration URI/version/SHA/cache ID and context;
- input and working spaces;
- ordered transforms and whether each was actually applied;
- display/view and whether the view was baked;
- output primaries, transfer, matrix, range, and bit depth;
- exact input and output artifact hashes.

Unknown AI-source color may be handled under a declared controlled SDR assumption. Do not
describe unknown bytes as measured scene-linear or color-managed source truth. A valid
receipt does not prove that the creative grade is attractive.

### Audio receipt

Record at least:

- exact source stem hashes, sample rate/format, channels/layout, and duration in samples;
- processing tools/versions, ordered operations, and gain changes;
- selected delivery profile and loudness-meter standard/tool;
- integrated loudness, maximum short-term loudness, and maximum true peak;
- audiovisual sync result and exact audio-master hash.

Do not treat a broadcast normalization target as a universal social-platform target.
Dialogue intelligibility, emotion, noise, music balance, and impact remain human review
items. Normalization or remixing creates a new artifact.

### Subtitle and delivery receipts

Bind subtitle language, source transcript hash, format, timebase, timing/coverage check,
safe-area/readability review, and whether subtitles are sidecar or burned in. A text,
timing, font, placement, or burn-in change creates new bytes and invalidates downstream
review.

The delivery profile declares destination, dimensions, frame rate, codec/container, pixel
format, color metadata, audio format/layout, and the selected measurement limits. Final QC
binds its report to both that profile and the exact delivery-master SHA.

## Final human hash gate

`required_final_gate_ids` must be nonempty for `machine_pass` or any later delivery
status. `human_delivery_gate_id` names a separate current human gate for
`human_approved` or `delivered`. Delivery requires at least:

- one current machine gate that binds both the exact delivery-master SHA and exact
  delivery-profile SHA;
- one current human gate that binds the exact delivery-master SHA under the recorded
  review conditions; and
- every ID in `required_final_gate_ids` present, current, and passing.

The human gate cannot satisfy the machine requirement, and a machine gate cannot grant
human approval. Provider success, assembly success, an empty gate list, an old proxy, a
filename, or an earlier encode is insufficient.

Any re-encode, crop, mix, subtitle change, watermark, signature, or color transform
creates a new delivery artifact and requires new final QC and human review.

## Invalidation and next action

An invalidation event records:

```text
invalidation_id, cause_artifact_id, cause_sha256, reason,
affected_artifact_ids, affected_shot_ids, affected_phases, recorded_at
```

When an artifact is rejected, stale, revoked, or superseded, traverse all dependency
edges and mark every descendant stale, rejected, or superseded. Selected takes, timeline,
finish receipts, final QC, and delivery cannot retain descendants of an invalid root.

`next_action` names the earliest affected phase, its owner, the bounded action, blockers,
and whether external mutation is allowed. Missing authorization, unresolved submission,
stale lineage, or incomplete gates force `external_mutation_allowed=false`.
`mode=audit_only` also forces it false regardless of any older authorization entry.

Each append-only `transition_log` event records:

```text
transition_id, from_phase, from_status, to_phase, to_status,
transition_kind, at, actor, evidence_artifact_ids, invalidation_ids
```

Forward transitions advance at most one canonical phase and require that destination's
gate coverage. A backward transition is `repair` and names its invalidation. Events are
time-ordered, each starts from the prior event's destination, and the last destination
equals current `state`. An empty or discontinuous log cannot evidence current state.

## What structural validation can and cannot prove

A future deterministic validator may check schema, paths, hashes, acyclicity, gate
bindings, authorization, integer-frame arithmetic, selected-take completeness,
invalidation propagation, and final-master evidence. Until such a validator is actually
implemented and integrated, perform these as an explicit audit and do not claim automated
enforcement.

Even a structural PASS would not prove story quality, identity, acting, motion physics,
camera taste, grade taste, sound taste, or human acceptance.
