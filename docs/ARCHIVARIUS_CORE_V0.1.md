# Archivarius Core v0.1

## Scope

Archivarius is a multimodal knowledge-ingestion and provenance system. It may ingest dictionaries, encyclopedias, mathematics, physics, chemistry, biology, text, code, images, audio, video, and structured data.

## Canonical entities

- `source`: origin, license, version, and retrieval metadata.
- `document`: raw or referenced source object.
- `lexeme`: language-specific word form.
- `sense`: meaning of a lexeme in context.
- `concept`: language-independent conceptual node.
- `entity`: concrete object, process, person, place, artifact, or event.
- `claim`: subject-predicate-object assertion with provenance.
- `relation`: typed edge between nodes.
- `observation`: extracted feature or measured value.

## Provenance

Every extracted claim must retain source, source version, extractor, confidence, timestamp, and review status. Extracted, inferred, verified, and contradicted assertions are distinct statuses.

## TAHI role

TAHI is a derived exact index for typed features, numeric ranges, temporal windows, categorical encodings, confidence thresholds, and other formal predicates. The canonical store remains authoritative; indexes are rebuildable snapshots.

## Ingestion pipeline

1. Register source and license.
2. Store or reference raw object by stable content hash.
3. Extract entities, features, and candidate claims.
4. Normalize into canonical schemas.
5. Validate and attach provenance.
6. Commit canonical records.
7. Build derived graph and TAHI snapshots.
8. Verify exact query results against canonical predicates.
