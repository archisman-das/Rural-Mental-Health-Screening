# Project Proposal

## Title

Rural Mental Health Screening AI: A Multilingual, Multimodal, Offline-Ready Screening Platform for Community and Primary-Care Settings

## Executive Summary

This project proposes a practical screening platform for rural and low-resource mental health workflows. The system is designed to support a real-world screening session from start to finish: capturing profile information, collecting questionnaire responses, interpreting narrative text, optionally using audio and image inputs, handling passive biomarker signals, producing recommendation text, storing the assessment, generating a PDF, and allowing later record review.

The repository already contains a working dashboard and backend implementation. This document describes the project as a formal proposal so the architecture can be explained clearly for research, evaluation, deployment planning, and future publication.

## Problem Context

Rural mental health screening is difficult for several reasons:

- specialist access is limited,
- follow-up documentation is often fragmented,
- internet connectivity may be unstable,
- patients may speak different languages,
- health workers need short, actionable outputs,
- records often need to be reviewed later in a report-friendly format.

Most digital tools do not solve all of these at once. Some tools only provide a score. Some are not multilingual. Some rely fully on stable internet access. Some generate results but do not explain them in a form a community health worker can use.

This project addresses those gaps by combining:

- multilingual screening,
- multimodal signal handling,
- offline fallback behavior,
- report generation,
- record management,
- quality-check reporting,
- and research-ready documentation.

## Core Proposal

The proposal is to build and evaluate a browser-based and backend-supported screening platform that can assist community health workers and primary-care teams in capturing and reviewing mental health screening data.

The platform should:

1. work in English, Hindi, and Bengali,
2. support structured questionnaires and narrative input,
3. optionally use audio, image, and passive biomarker signals,
4. give a clear recommendation and screening disclaimer,
5. save assessments for later retrieval,
6. export PDF reports,
7. continue to function in limited form when the backend is offline,
8. provide quality-check and model-statistics views for transparency.

## Why This Matters

The main value of the project is not only prediction accuracy. It is the complete workflow.

The system aims to:

- reduce friction for front-line screening,
- make the output understandable,
- preserve the record for follow-up,
- support language access,
- and keep the app useful even when the network is unreliable.

That combination is especially relevant in rural or community settings.

## Proposed System Design

### Frontend

The frontend is responsible for:

- language switching,
- profile and questionnaire entry,
- narrative input,
- optional media capture,
- adaptive test flow,
- preview rendering,
- result interpretation,
- records and reports browsing,
- record deletion,
- report hiding,
- offline status messaging.

### Backend

The Flask backend is responsible for:

- validating assessment input,
- computing preview and saved assessment results,
- persisting records,
- serving record lookup and deletion,
- generating PDFs,
- exposing model statistics,
- running quality checks,
- serving sample and database metadata,
- supporting adaptive screening requests.

### Core Logic

The core Python package handles:

- questionnaire definitions,
- feature extraction,
- inference and confidence estimation,
- storage,
- PDF reporting,
- training and bundle generation,
- model metadata summarization.

## Functional Workflow

The system works in this order:

1. The user selects a language.
2. The user enters profile details and consent.
3. The user completes the questionnaire.
4. The user adds a narrative description.
5. Optional audio, image, or passive biomarker inputs are added.
6. The dashboard generates a live preview.
7. The user saves the assessment.
8. The record appears in the records and analytics views.
9. The user can later fetch, export, delete, or hide the record.

If the backend is unavailable, the dashboard can still show a limited preview and queue the record for later sync.

## Proposed Technical Method

The system combines multiple evidence sources:

- questionnaire domain scores,
- narrative NLP,
- speech or audio metadata,
- facial/image metadata,
- passive biomarker traces,
- trained bundle metadata,
- fallback heuristics when trained inference is unavailable.

The final output includes:

- per-domain risk labels,
- overall confidence,
- recommendation text,
- screening disclaimer,
- modality quality summaries,
- trajectory and trend information.

## Multilingual Strategy

The UI is designed so the active language changes more than labels. It also changes:

- validated instrument display,
- recommendations,
- disclaimers,
- offline messages,
- quality-check explanations,
- and adaptive-screening prompts.

This matters because a mental health screening tool must be understandable to the actual user, not only technically correct.

## ONNX and Bundle Strategy

The repository now keeps both:

- the original pickle bundles,
- and the exported ONNX artifacts.

This is useful because it preserves compatibility while also making deployment and portability easier for supported estimators.

The ONNX files live under:

- `models/mental_health_screening/onnx/`

The export tool is:

- `tools/export_model_bundles_to_onnx.py`

## Evaluation Plan

The project should be evaluated with:

- accuracy,
- macro F1,
- calibration or Brier score,
- ROC AUC where appropriate,
- offline success rate,
- adaptive completion rate,
- usability feedback,
- multilingual consistency,
- record completeness.

The strongest evaluation approach is an ablation study:

- questionnaire only,
- questionnaire + text,
- questionnaire + text + audio,
- questionnaire + text + image,
- questionnaire + text + audio + image + passive,
- backend mode versus offline fallback mode.

## Ethics and Safety

The system is a screening tool, not a diagnosis engine.

The proposal requires that:

- consent be obtained,
- demo data be excluded from clinical claims,
- records be treated with privacy protection,
- disclaimer text be explicit,
- emergency escalation pathways remain clear,
- the system not overstate certainty.

## Risks

Technical risks include:

- missing model bundles,
- backend downtime,
- unstable connectivity,
- incomplete media capture,
- conversion issues between formats.

Research risks include:

- dataset bias,
- limited multilingual coverage,
- proxy-data mismatch,
- overfitting,
- poor subgroup calibration.

Mitigation includes:

- offline fallback logic,
- local queueing,
- ONNX and pickle coexistence,
- quality checks,
- error analysis,
- transparent reporting.

## Expected Deliverables

The project should produce:

- a working multilingual dashboard,
- adaptive screening,
- backend APIs,
- PDF reports,
- trajectory and quality-check views,
- documentation,
- research proposals,
- paper scaffolding,
- ONNX exports,
- reproducible evaluation scripts.

## Conclusion

This project proposal frames the repository as a full screening system rather than just a model. It is designed for usability, traceability, multilingual access, and future research validation. The current implementation already provides a strong base for publication, field testing, and operational deployment.

