import streamlit as st
import tempfile
import os

from interview_data import QUESTIONS
from evaluator import evaluate_answer
from speech_to_text import transcribe_audio
from voice_analysis import analyze_voice
from report import create_report


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #f7f7f8;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.ai-logo {
    width: 120px;
    height: 120px;
    margin: 80px auto 25px auto;
    border-radius: 50%;
    background: linear-gradient(
        135deg,
        #10a37f,
        #19c37d
    );
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 60px;
    box-shadow:
        0px 10px 35px rgba(0,0,0,0.18);
}

.entrance-title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 10px;
}

.entrance-subtitle {
    text-align: center;
    font-size: 18px;
    color: #666666;
    margin-bottom: 35px;
}

.question-card {
    background: white;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #e5e5e5;
    margin-top: 15px;
    margin-bottom: 20px;
    box-shadow:
        0px 3px 12px rgba(0,0,0,0.05);
}

.app-card {
    background: white;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #e5e5e5;
    box-shadow:
        0px 3px 12px rgba(0,0,0,0.05);
}

section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e5e5e5;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {

    "page": "welcome",

    "name": "",
    "phone": "",
    "email": "",

    "role": "",

    "level_index": 0,
    "question_index": 0,

    "answers": {},
    "results": {},
    "voice_results": {},

    # NEW: Store recorded audio
    "audio_results": {},

    "total_score": 0,
    "correct_answers": 0
}


for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# LEVELS
# =========================================================

levels = [
    "Basic",
    "Intermediate",
    "Hard"
]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_question_id():

    return (
        f"{st.session_state.level_index}_"
        f"{st.session_state.question_index}"
    )


def reset_interview():

    st.session_state.level_index = 0

    st.session_state.question_index = 0

    st.session_state.answers = {}

    st.session_state.results = {}

    st.session_state.voice_results = {}

    # NEW
    st.session_state.audio_results = {}

    st.session_state.total_score = 0

    st.session_state.correct_answers = 0


def calculate_final_score():

    total = 0
    correct = 0

    for result in st.session_state.results.values():

        total += result["score"]

        if result["score"] >= 5:
            correct += 1

    return total, correct


# =========================================================
# SIDEBAR
# =========================================================

if st.session_state.page != "welcome":

    with st.sidebar:

        st.markdown(
            """
            <h2 style="
                text-align:center;
                margin-bottom:25px;
            ">
            🤖 AI Interview
            </h2>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")


        # Candidate Details

        if st.button(
            "👤  Candidate Details",
            use_container_width=True
        ):

            st.session_state.page = "details"

            st.rerun()


        # Interview Role

        if st.button(
            "💼  Interview Role",
            use_container_width=True
        ):

            st.session_state.page = "role"

            st.rerun()


        # Interview

        if st.button(
            "🎤  Interview",
            use_container_width=True
        ):

            if not st.session_state.name:

                st.session_state.page = "details"

            elif not st.session_state.role:

                st.session_state.page = "role"

            else:

                st.session_state.page = "interview"

            st.rerun()


        # Final Report

        if st.button(
            "🏆  Final Report",
            use_container_width=True
        ):

            if len(st.session_state.results) == 0:

                st.warning(
                    "Complete the interview first."
                )

            else:

                st.session_state.page = "report"

                st.rerun()


        st.markdown("---")


        st.caption(
            "CURRENT CANDIDATE"
        )


        if st.session_state.name:

            st.write(
                f"👤 {st.session_state.name}"
            )

        else:

            st.write(
                "Not entered"
            )


        st.caption(
            "INTERVIEW ROLE"
        )


        if st.session_state.role:

            st.write(
                f"💼 {st.session_state.role}"
            )

        else:

            st.write(
                "Not selected"
            )


# =========================================================
# ENTRANCE PAGE
# =========================================================

if st.session_state.page == "welcome":

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        st.markdown(
            '<div class="ai-logo">🤖</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="entrance-title">
                AI Interview Assistant
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="entrance-subtitle">
                Your personal AI-powered interview practice
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")


        if st.button(
            "🚀 Start Interview",
            use_container_width=True
        ):

            st.session_state.page = "details"

            st.rerun()


# =========================================================
# CANDIDATE DETAILS
# =========================================================

elif st.session_state.page == "details":

    st.title(
        "👤 Candidate Details"
    )

    st.caption(
        "Tell us a little about yourself before the interview."
    )

    st.markdown("---")


    name = st.text_input(
        "Full Name",
        value=st.session_state.name,
        placeholder="Enter your full name"
    )


    phone = st.text_input(
        "Mobile Number",
        value=st.session_state.phone,
        placeholder="Enter your mobile number"
    )


    email = st.text_input(
        "Email Address",
        value=st.session_state.email,
        placeholder="Enter your email address"
    )


    st.write("")


    if st.button(
        "Continue →",
        use_container_width=True
    ):

        if not name.strip():

            st.error(
                "Please enter your name."
            )

        elif not phone.strip():

            st.error(
                "Please enter your mobile number."
            )

        elif not email.strip():

            st.error(
                "Please enter your email address."
            )

        else:

            st.session_state.name = name.strip()

            st.session_state.phone = phone.strip()

            st.session_state.email = email.strip()

            st.session_state.page = "role"

            st.rerun()


# =========================================================
# INTERVIEW ROLE
# =========================================================

elif st.session_state.page == "role":

    st.title(
        "💼 Interview Role"
    )

    st.caption(
        "Choose the role you want to practice for."
    )

    st.markdown("---")


    if not st.session_state.name:

        st.warning(
            "Please complete Candidate Details first."
        )


        if st.button(
            "Go to Candidate Details",
            use_container_width=True
        ):

            st.session_state.page = "details"

            st.rerun()

    else:

        st.success(
            f"Welcome, {st.session_state.name}"
        )


        role = st.selectbox(
            "Select Interview Role",
            list(QUESTIONS.keys())
        )


        st.write("")


        if st.button(
            "Continue →",
            use_container_width=True
        ):

            st.session_state.role = role

            reset_interview()

            st.session_state.page = "interview"

            st.rerun()


# =========================================================
# INTERVIEW PAGE
# =========================================================

elif st.session_state.page == "interview":

    if not st.session_state.name:

        st.session_state.page = "details"

        st.rerun()


    elif not st.session_state.role:

        st.session_state.page = "role"

        st.rerun()


    else:

        role = st.session_state.role


        level = levels[
            st.session_state.level_index
        ]


        questions = QUESTIONS[
            role
        ][
            level
        ]


        question_index = (
            st.session_state.question_index
        )


        question_data = questions[
            question_index
        ]


        question_id = get_question_id()


        question_number = (
            st.session_state.level_index * 5
            + st.session_state.question_index
            + 1
        )


        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        st.title(
            "🎤 Interview"
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.caption("ROLE")

            st.write(
                f"💼 {role}"
            )


        with col2:

            st.caption("LEVEL")

            st.write(
                f"📚 {level}"
            )


        with col3:

            st.caption("QUESTION")

            st.write(
                f"❓ {question_number} / 15"
            )


        st.progress(
            question_number / 15
        )


        st.markdown("---")


        # -------------------------------------------------
        # QUESTION
        # -------------------------------------------------

        st.markdown(
            f"""
            <div class="question-card">

                <small>
                    QUESTION {question_number}
                </small>

                <h2>
                    {question_data['question']}
                </h2>

            </div>
            """,
            unsafe_allow_html=True
        )


        already_answered = (
            question_id
            in st.session_state.results
        )


        # =================================================
        # ANSWER INPUT
        # =================================================

        if not already_answered:

            previous_answer = (
                st.session_state.answers.get(
                    question_id,
                    ""
                )
            )


            answer = st.text_area(
                "⌨️ Your Answer",
                value=previous_answer,
                key=f"answer_{question_id}",
                height=170,
                placeholder="Type your answer here..."
            )


            st.markdown("---")


            st.subheader(
                "🎙️ Voice Answer"
            )


            st.caption(
                "You can answer by speaking instead of typing."
            )


            audio_file = st.audio_input(
                "Record your answer",
                key=f"audio_{question_id}"
            )


            st.write("")


            if st.button(
                "✅ Submit Answer",
                use_container_width=True
            ):

                final_answer = answer.strip()

                temporary_audio = None


                # -----------------------------------------
                # VOICE PROCESSING
                # -----------------------------------------

                if audio_file is not None:

                    try:

                        # Save audio bytes in session
                        audio_bytes = (
                            audio_file.getvalue()
                        )


                        st.session_state.audio_results[
                            question_id
                        ] = audio_bytes


                        # Temporary file for processing
                        with tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=".wav"
                        ) as temp:

                            temp.write(
                                audio_bytes
                            )

                            temporary_audio = (
                                temp.name
                            )


                        st.info(
                            "🎧 Processing voice..."
                        )


                        # Whisper transcription
                        voice_text = (
                            transcribe_audio(
                                temporary_audio
                            )
                        )


                        # Librosa analysis
                        voice_features = (
                            analyze_voice(
                                temporary_audio
                            )
                        )


                        st.session_state.voice_results[
                            question_id
                        ] = voice_features


                        # If no typed answer,
                        # use voice transcription
                        if not final_answer:

                            final_answer = (
                                voice_text
                            )


                            st.subheader(
                                "🗣️ Transcription"
                            )


                            st.info(
                                voice_text
                            )


                    except Exception as error:

                        st.error(
                            f"Voice processing error: {error}"
                        )


                    finally:

                        if (
                            temporary_audio
                            and os.path.exists(
                                temporary_audio
                            )
                        ):

                            os.remove(
                                temporary_audio
                            )


                # -----------------------------------------
                # EMPTY ANSWER
                # -----------------------------------------

                if not final_answer:

                    st.warning(
                        "Please type an answer or record your voice."
                    )


                else:

                    # -------------------------------------
                    # EVALUATION
                    # -------------------------------------

                    result = evaluate_answer(
                        final_answer,
                        question_data
                    )


                    st.session_state.answers[
                        question_id
                    ] = final_answer


                    st.session_state.results[
                        question_id
                    ] = result


                    total, correct = (
                        calculate_final_score()
                    )


                    st.session_state.total_score = (
                        total
                    )


                    st.session_state.correct_answers = (
                        correct
                    )


                    st.rerun()


        # =================================================
        # ANSWER RESULT
        # =================================================

        else:

            saved_answer = (
                st.session_state.answers[
                    question_id
                ]
            )


            result = (
                st.session_state.results[
                    question_id
                ]
            )


            # -------------------------------------------------
            # SAVED ANSWER
            # -------------------------------------------------

            st.subheader(
                "📝 Your Answer"
            )


            st.info(
                saved_answer
            )


            # -------------------------------------------------
            # AUDIO PLAYBACK
            # -------------------------------------------------

            if (
                question_id
                in st.session_state.audio_results
            ):

                st.subheader(
                    "🎧 Your Recorded Answer"
                )


                st.audio(
                    st.session_state.audio_results[
                        question_id
                    ],
                    format="audio/wav"
                )


            # -------------------------------------------------
            # EVALUATION
            # -------------------------------------------------

            st.subheader(
                "📊 Evaluation"
            )


            score = result[
                "score"
            ]


            if score >= 8:

                st.success(
                    f"⭐ Score: {score}/10"
                )

            elif score >= 5:

                st.warning(
                    f"⭐ Score: {score}/10"
                )

            else:

                st.error(
                    f"⭐ Score: {score}/10"
                )


            st.write(
                result["feedback"]
            )


            # -------------------------------------------------
            # EXPECTED ANSWER
            # -------------------------------------------------

            st.subheader(
                "✅ Expected Answer"
            )


            st.info(
                result["correct_answer"]
            )


            # -------------------------------------------------
            # CONCEPTS
            # -------------------------------------------------

            if result["matched"]:

                st.subheader(
                    "🔑 Concepts Detected"
                )


                st.write(
                    ", ".join(
                        result["matched"]
                    )
                )


            # -------------------------------------------------
            # VOICE TRANSCRIPTION
            # -------------------------------------------------

            if (
                question_id
                in st.session_state.voice_results
            ):

                # We don't store transcription separately,
                # so playback + analysis are shown here.

                st.subheader(
                    "🎙️ Voice Analysis"
                )


                features = (
                    st.session_state.voice_results[
                        question_id
                    ]
                )


                col1, col2, col3 = st.columns(3)


                with col1:

                    st.metric(
                        "Duration",
                        f"{features['duration']} sec"
                    )


                with col2:

                    st.metric(
                        "Average Volume",
                        features[
                            "average_volume"
                        ]
                    )


                with col3:

                    st.metric(
                        "Voice Activity",
                        features[
                            "zero_crossing_rate"
                        ]
                    )


                st.caption(
                    "These are audio delivery indicators, not a psychological measurement of confidence."
                )


        # =================================================
        # NAVIGATION
        # =================================================

        st.markdown("---")


        col1, col2 = st.columns(2)


        # -------------------------------------------------
        # PREVIOUS
        # -------------------------------------------------

        with col1:

            if (
                st.session_state.level_index > 0
                or
                st.session_state.question_index > 0
            ):

                if st.button(
                    "← Previous",
                    use_container_width=True
                ):

                    if (
                        st.session_state.question_index
                        > 0
                    ):

                        st.session_state.question_index -= 1

                    else:

                        st.session_state.level_index -= 1

                        st.session_state.question_index = 4


                    st.rerun()


        # -------------------------------------------------
        # NEXT
        # -------------------------------------------------

        with col2:

            if (
                st.session_state.question_index
                < 4
            ):

                if st.button(
                    "Next →",
                    use_container_width=True
                ):

                    st.session_state.question_index += 1

                    st.rerun()


            elif (
                st.session_state.level_index
                < 2
            ):

                next_level = levels[
                    st.session_state.level_index + 1
                ]


                if st.button(
                    f"Continue to {next_level} →",
                    use_container_width=True
                ):

                    st.session_state.level_index += 1

                    st.session_state.question_index = 0

                    st.rerun()


            else:

                if st.button(
                    "🏆 View Final Report",
                    use_container_width=True
                ):

                    st.session_state.page = "report"

                    st.rerun()


# =========================================================
# FINAL REPORT
# =========================================================

elif st.session_state.page == "report":

    st.title(
        "🏆 Interview Report"
    )


    total_score, correct_answers = (
        calculate_final_score()
    )


    maximum_score = 150


    percentage = round(
        (
            total_score
            /
            maximum_score
        )
        * 100
    )


    report = create_report(
        st.session_state.name,
        st.session_state.role,
        total_score,
        maximum_score,
        correct_answers,
        15
    )


    # =====================================================
    # CANDIDATE
    # =====================================================

    st.subheader(
        "👤 Candidate"
    )


    col1, col2 = st.columns(2)


    with col1:

        st.write(
            f"**Name:** "
            f"{st.session_state.name}"
        )


        st.write(
            f"**Mobile:** "
            f"{st.session_state.phone}"
        )


    with col2:

        st.write(
            f"**Email:** "
            f"{st.session_state.email}"
        )


        st.write(
            f"**Role:** "
            f"{st.session_state.role}"
        )


    st.markdown("---")


    # =====================================================
    # SCORE
    # =====================================================

    st.subheader(
        "📊 Performance"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Score",
            report["Score"]
        )


    with col2:

        st.metric(
            "Percentage",
            report["Percentage"]
        )


    with col3:

        st.metric(
            "Passed",
            report["Correct/Passed"]
        )


    st.progress(
        percentage / 100
    )


    # =====================================================
    # FEEDBACK
    # =====================================================

    st.subheader(
        "🤖 Interview Feedback"
    )


    if percentage >= 80:

        st.success(
            "Excellent performance. "
            "Your technical concepts are well developed."
        )

    elif percentage >= 60:

        st.info(
            "Good performance. "
            "Continue improving your technical explanations."
        )

    elif percentage >= 40:

        st.warning(
            "You have a foundation. "
            "Practice the concepts and explain answers "
            "in more detail."
        )

    else:

        st.error(
            "More preparation is recommended. "
            "Review the fundamentals and practice again."
        )


    # =====================================================
    # NEW INTERVIEW
    # =====================================================

    st.markdown("---")


    if st.button(
        "🔄 Start New Interview",
        use_container_width=True
    ):

        st.session_state.name = ""

        st.session_state.phone = ""

        st.session_state.email = ""

        st.session_state.role = ""

        reset_interview()

        st.session_state.page = "welcome"

        st.rerun()