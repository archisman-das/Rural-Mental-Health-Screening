import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
SYS_PATH = str(ROOT / "src")
if SYS_PATH not in sys.path:
    sys.path.append(SYS_PATH)

from mental_health_screening.assessment import get_question_bank, get_response_options, score_questionnaire
from mental_health_screening.constants import PREDICTION_LABELS
from mental_health_screening.constants import PREDICTION_DOMAINS
from mental_health_screening.feature_extract import save_upload_file
from mental_health_screening.predict import screen
from mental_health_screening.report import create_assessment_pdf_bytes
from mental_health_screening.storage import create_assessment_record, fetch_assessment_record, get_database_metadata


st.set_page_config(page_title="Rural Mental Health Screening", page_icon="MH", layout="wide")


def cleanup_temp_file(path: str | None) -> None:
    if path and os.path.exists(path):
        os.remove(path)


def render_domain_metrics(result: dict, suffix: str) -> None:
    columns = st.columns(3)
    for index, domain in enumerate(PREDICTION_DOMAINS):
        key = domain if not suffix else f"{domain}_{suffix}"
        columns[index % 3].metric(
            PREDICTION_LABELS[domain],
            str(result[key]).capitalize() if suffix == "risk" else str(result[key]).capitalize(),
        )


def render_result_view(record: dict) -> None:
    questionnaire = record["questionnaire"]
    multimodal = record["multimodal"]
    overall = multimodal["overall"]

    st.success(f"Assessment found: {record['assessment_id']}")
    st.caption(f"Submitted at {record['created_at']}")

    st.subheader("Candidate Profile")
    st.json(record["profile"])

    st.subheader("Questionnaire Result")
    render_domain_metrics(questionnaire, "risk")
    st.metric("Overall Score", f"{questionnaire['overall_score']:.2f}")

    st.subheader("Multimodal Screening Result")
    render_domain_metrics(overall, "")
    st.metric("Confidence", f"{overall['confidence']:.0%}")

    score_cols = st.columns(2)
    left_domains = PREDICTION_DOMAINS[::2]
    right_domains = PREDICTION_DOMAINS[1::2]
    for domain in left_domains:
        score_cols[0].progress(overall["scores"][domain], text=f"{PREDICTION_LABELS[domain]} score")
    for domain in right_domains:
        score_cols[1].progress(overall["scores"][domain], text=f"{PREDICTION_LABELS[domain]} score")

    st.subheader("Recommendation")
    st.write(multimodal["recommendation"])
    st.caption(multimodal["disclaimer"])

    pdf_bytes = create_assessment_pdf_bytes(record)
    st.download_button(
        "Download PDF Report",
        data=pdf_bytes,
        file_name=f"{record['assessment_id']}_report.pdf",
        mime="application/pdf",
    )


st.title("Rural Mental Health Screening AI")
st.write(
    "A web-based screening system for rural mental health outreach. Users can complete an online test, submit optional speech and image inputs, and fetch saved results later using an assessment ID."
)
st.caption(
    "Current prediction scope: Depression, Anxiety, Stress, Sleep Disorder, Burnout, Loneliness, and Substance Abuse."
)

stack_col, db_col = st.columns(2)
with stack_col:
    st.info("Frontend: Streamlit | NLP backend: PyTorch-powered transformer pipeline with heuristic fallbacks")
with db_col:
    metadata = get_database_metadata()
    st.info(
        f"Database: {metadata['database']} | Stored records: {metadata['total_records']} | Cache sync: JSON for dashboard compatibility"
    )

intro_left, intro_right = st.columns([1.3, 1.0])
with intro_left:
    st.markdown(
        "- Use the `Take Online Test` tab to conduct a structured screening session.\n"
        "- The system stores the result and generates an assessment ID.\n"
        "- Use the `Fetch Result` tab to retrieve the result later for the end user."
    )
with intro_right:
    st.info(
        "This is a screening and triage prototype only. It should support, not replace, a clinician or trained community health worker."
    )

test_tab, fetch_tab = st.tabs(["Take Online Test", "Fetch Result"])

with test_tab:
    st.subheader("Online Mental Health Test")
    st.caption("Complete the questionnaire below, then optionally add speech and facial inputs.")

    with st.form("online_screening_form"):
        profile_col, context_col = st.columns(2)

        with profile_col:
            full_name = st.text_input("Full name")
            age = st.number_input("Age", min_value=10, max_value=100, value=25)
            gender = st.selectbox("Gender", ["Prefer not to say", "Female", "Male", "Other"])
            village = st.text_input("Village / Local area")

        with context_col:
            phone = st.text_input("Phone or reference number")
            assessor = st.text_input("Assessor / Health worker name")
            language = st.selectbox("Preferred language", ["English", "Hindi", "Bengali", "Other"])
            consent = st.checkbox("Consent received for screening and optional uploads")

        st.markdown("### Symptom Questionnaire")
        response_options = list(get_response_options().keys())
        questionnaire_answers = {}
        current_section = None
        for question in get_question_bank():
            if question["section"] != current_section:
                current_section = question["section"]
                st.markdown(f"#### {current_section}")
            questionnaire_answers[question["id"]] = st.radio(
                question["prompt"],
                response_options,
                horizontal=True,
            )

        st.markdown("### Optional AI Inputs")
        text_input = st.text_area(
            "Describe how you have been feeling recently",
            height=180,
            placeholder="Example: I have been feeling tense, low on energy, and unable to sleep properly.",
        )
        audio_file = st.file_uploader(
            "Upload a short voice sample",
            type=["wav", "mp3", "m4a"],
            help="Best if 15 to 30 seconds, recorded in a quiet place.",
        )
        image_file = st.file_uploader(
            "Upload a face image",
            type=["png", "jpg", "jpeg"],
            help="Front-facing image with clear lighting, only if consent is available.",
        )

        submit_test = st.form_submit_button("Submit Assessment")

    if submit_test:
        if not consent:
            st.warning("Please confirm consent before submitting the online screening.")
        else:
            audio_path = None
            image_path = None

            if audio_file is not None:
                audio_path = save_upload_file(audio_file, suffix="audio")
            if image_file is not None:
                image_path = save_upload_file(image_file, suffix="image")

            try:
                numeric_answers = {
                    question_id: get_response_options()[selected]
                    for question_id, selected in questionnaire_answers.items()
                }
                questionnaire_result = score_questionnaire(numeric_answers)
                multimodal_result = screen(
                    text_input=text_input,
                    audio_path=audio_path,
                    image_path=image_path,
                )
                profile = {
                    "full_name": full_name,
                    "age": int(age),
                    "gender": gender,
                    "village": village,
                    "phone": phone,
                    "assessor": assessor,
                    "language": language,
                }
                record = create_assessment_record(
                    profile=profile,
                    questionnaire=questionnaire_result,
                    multimodal=multimodal_result,
                )
            finally:
                cleanup_temp_file(audio_path)
                cleanup_temp_file(image_path)

            st.success("Assessment submitted successfully.")
            st.code(record["assessment_id"], language="text")
            st.caption("Use this assessment ID in the Fetch Result tab to retrieve the stored result later.")
            render_result_view(record)

with fetch_tab:
    st.subheader("Fetch Saved Result")
    assessment_id = st.text_input("Enter assessment ID", placeholder="Example: MHS-1A2B3C4D")
    if st.button("Fetch Assessment Result"):
        if not assessment_id.strip():
            st.warning("Please enter a valid assessment ID.")
        else:
            record = fetch_assessment_record(assessment_id)
            if record is None:
                st.error("No saved assessment was found for that ID.")
            else:
                render_result_view(record)
