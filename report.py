def create_report(
    name,
    role,
    total_score,
    maximum_score,
    correct_answers,
    total_questions
):

    percentage = round(
        (total_score / maximum_score) * 100
    )

    report = {
        "Candidate": name,
        "Role": role,
        "Total Questions": total_questions,
        "Correct/Passed": correct_answers,
        "Score": f"{total_score}/{maximum_score}",
        "Percentage": f"{percentage}%"
    }

    return report