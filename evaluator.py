def evaluate_answer(user_answer, question_data):

    user_answer = user_answer.lower()

    keywords = question_data["keywords"]

    matched_keywords = []

    for keyword in keywords:

        if keyword.lower() in user_answer:
            matched_keywords.append(keyword)

    if len(keywords) == 0:
        score = 0
    else:
        score = round(
            (len(matched_keywords) / len(keywords)) * 10
        )

    if score > 10:
        score = 10

    if score >= 8:

        feedback = (
            "Excellent answer. You covered most of the important concepts."
        )

    elif score >= 5:

        feedback = (
            "Good attempt. Your answer contains some important concepts, "
            "but you can provide more details."
        )

    else:

        feedback = (
            "Needs improvement. Review the concept and try to include "
            "the important points."
        )

    return {
        "score": score,
        "matched": matched_keywords,
        "feedback": feedback,
        "correct_answer": question_data["answer"]
    }