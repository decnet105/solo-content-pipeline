# Native AI motion production contract

Use this contract when a shot depends on generated body movement, facial acting,
dialogue, contact, prop handling or cross-shot continuity. The starter scripts do not
enforce it automatically; treat it as a preflight and evidence record around the existing
provider callers.

The current `make_short.py` generated-video path is not an executor for this contract: it
uses one start image, a fixed four-second request and a `face_free` switch, without
separate identity/look/interaction/motion bindings or durable task recovery. For a
character-led request, fail closed until an adapter can represent and persist the fields
below. Do not silently substitute a Ken Burns still and call it animation.

## Keep four layers separate

1. **Story and shot intent** — what changes in the scene and what the audience must read.
2. **Continuity assets** — approved identity, wardrobe/look, environment, expression,
   interaction, motion and audio references.
3. **Provider adapter** — the current model, endpoint, labels, limits and compiled prompt.
4. **Output evidence** — the exact downloaded file, technical probe, review and verdict.

A prompt is an adapter artifact, not source truth. Do not repair a missing story,
identity, action or environment decision by improvising inside the provider prompt.

## One continuous shot per request

One paid request should describe one uninterrupted photographic shot. The contract needs:

- `shot_id`, purpose and source/story anchor;
- exact duration, aspect ratio, resolution and audio expectation;
- start state, preparation, main action/contact, settling and end state;
- camera position, lens family, axis, movement and stop condition;
- visible subjects, gaze targets and facial reaction beats;
- feet/support, weight transfer, both hands, held props and contact points;
- environment state, light direction and continuity in/out;
- explicit forbidden drift.

Cuts, shot/reverse-shot, montage, subtitles, transitions, BGM and final pacing belong to
the edit/audio plan. Do not hide several shots inside one long “timecoded” provider
prompt.

## Bind every reference by purpose

Do not rely on array order. Record each exact asset path/hash, rights state, human status,
subject and one or more roles:

- `identity` — stable face/body geometry;
- `look` — wardrobe, hair, accessories and current condition;
- `expression` — a specific facial state or transition;
- `environment` — space, materials, set dressing and light state;
- `start_frame` / `end_frame` — composition and pose anchors;
- `interaction` — hands, contact topology and prop orientation;
- `motion_reference` — real-time body mechanics and timing;
- `temporal_structure` — an existing video used for rhythm or continuation;
- `audio_reference` — voice, dialogue, ambience or music behavior.

One contact sheet may help human review but should not silently become the machine input
for identity, look, motion and interaction at once. Provider labels such as `@Image1`
belong only in the adapter map.

## Reverse references without pretending to recover a prompt

A still image does not reveal its unique original prompt, model, seed, lens, renderer,
LoRA, LUT or upscale path. Separate:

- `E observed` — visible geometry, pose, gaze, contact, palette, light, perspective,
  line/paint grammar, materials and defects;
- `I inferred` — a plausible but non-unique explanation;
- `H hypothesized` — an instruction expected to reproduce one property;
- `unknown` — anything the pixels and provenance do not establish.

Convert observations into a model-neutral visual contract, then compile the selected
provider syntax. Do not use a named creator, studio, title, character or “same IP” as the
generation instruction; express rights-safe visual mechanisms instead.

## Paid-request gate and recovery

Before submission, bind:

- the approved shot and asset hashes;
- provider, model, endpoint revision and recently checked official capability source;
- request ID, immutable input digest and idempotency key;
- maximum paid attempts and maximum cost;
- retry classes and the location of the saved external task record.

Permit one paid attempt per authorized request. Upload, polling and download may retry
when they cannot start a new generation. Content-policy, rights, invalid-input, exhausted
budget, human rejection and hard-QC failures are terminal for the same request. If the
submit response is ambiguous, mark it for manual reconciliation; do not assume failure
and pay again.

Recommended state sequence:

```text
planned -> compiled -> preflight_passed -> submitted -> provider_complete
-> downloaded -> technical_pass -> candidate_pending_human_review
-> human_accepted | human_rejected
```

A URL can move the request only to `provider_complete`.

An ambiguous submit follows a blocking side branch:

```text
submitted -> submit_unknown -> reconciliation_required
```

It cannot return to `submitted` or enter assembly until the original task is reconciled.

## High-risk body and camera handling

For a turn, reach, step, impact, prop interaction or full-body reaction, use a
rights-cleared real-world reference at 1x speed. If the user cannot record a rehearsal,
that does not relax the gate. Use this three-layer route:

1. `external_screen_study` may use lawfully viewed films, television, anime or web clips
   to identify action phases and failure modes. Copyrighted screen media and ordinary
   YouTube access are mechanism evidence only, never automatic model-input permission.
2. `rights_cleared_motion_source` supplies the kinematic basis from user-owned,
   commissioned, public-domain or explicitly licensed footage/mocap. Verify the exact
   license, performer/likeness rights, AI-use restrictions and provider-input terms.
3. `shot_specific_neutral_proxy` retargets and authors the exact shot on a neutral rig.
   It must be faceless and voiceless and contain no original pixels, background, source
   audio or recognizable performer. Preserve only the required motion, contact and timing.

Break the action into anticipation, weight transfer, movement, contact, load
acceptance/braking and settle. Check the support foot, pelvis/root path, joint chain,
secondary motion and end pose. A rough 2D pose trace is only a `research_fixture`; it
cannot pass as a production proxy because it does not prove depth, balance, foot lock,
hand/prop contact or continuous whole-body mechanics.

For a character raising a camera, separately lock:

- right hand on the grip and left hand supporting the lens;
- the chosen viewfinder eye and visible eyecup contact;
- eye-level stop height and optical-axis target;
- planted-foot/load acceptance and the exact end condition.

Words such as “realistic,” high frame rate or optical-flow smoothness do not prove correct
mechanics.

## Neutral-proxy provenance and review

Store a canonical lineage record next to every production proxy. Use stable IDs and exact
hashes; do not replace these fields with prose:

```yaml
schema_version: "1.0"
reference_id: motion-ref-...
status: human_approved
raw_video_used_as_model_input: false # downstream generative request
sources:
  - source_id: source-...
    source_type: rights_cleared_motion_source # or external_screen_study
    source_url: https://...
    sha256: ... # when a local source file was lawfully retained
    license_name: ...
    license_url: https://...
    rights_status: rights_cleared # license_verified | public_domain | external_study_only
    use_role: kinematic_base # prop_handling | mechanism_only
    raw_video_used_as_model_input: false
transformations:
  - transformation_id: transform-...
    operation: pose_extract_retarget_author
    input_source_ids: [source-...]
exact_output:
  path: ...
  sha256: ...
  role: shot_specific_neutral_proxy
```

`external_study_only` may have only `mechanism_only`; at least one separately cleared
source must provide `kinematic_base` or `prop_handling`. Every transformation input must
resolve to a listed source, and `exact_output.sha256` must match the actual proxy file.

Bind a separate rights review to the same `reference_id` and proxy hash:

```yaml
status: rights_cleared_for_neutral_proxy_model_input
authority: ...
source_rights_confirmed: true
provider_input_rights_confirmed: true
original_pixels_not_bound: true
proxy_sha256: ...
reference_id: motion-ref-...
reviewer: ...
reviewed_at: ...
```

Then have a human watch the exact proxy at 1x and approve the action phases, root/weight,
feet, gaze, hands, prop/contact and end state against the shot contract. Bind that verdict
to the same hash. Fail the paid preflight when lineage or rights review is missing/stale,
the only basis is `external_screen_study`, the artifact is a 2D research fixture, the 1x
motion review is missing/rejected, the provider cannot bind the proxy by role, or current
cost authorization is absent.

## Exact-output acceptance

Download and hash the raw output; make any review transcode separately and record the
transform. Probe duration, frame rate, dimensions, codec, color and audio. Then watch the
entire exact file at normal speed and intended size with sound.

Review at least:

- story action and timing;
- identity, wardrobe and accessories across all frames;
- face visibility, gaze target and causal expression change;
- support/contact, hands, props and normal-speed physics;
- camera/space/light continuity;
- dialogue, ambience, music and unwanted text/watermarks.

Automated checks locate defects; they do not award the artistic verdict. Only a current
human approval bound to the exact output hash may enter assembly. Missing or rejected
shots remain fatal; never skip them and call the film complete.
