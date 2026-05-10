import uuid
from datetime import date

from app.schemas.surveys_scheme import (
    SurveyCreate,
    SurveyResponse,
    QuestionInSurvey,
    SurveyWithQuestions
)


class TestSurveySchemas:

    def test_survey_create(self):

        survey = SurveyCreate(
            name="Encuesta Burnout",
            aperture_date=date(2026, 1, 1),
            finishing_date=date(2026, 1, 30),
            status="Activa"
        )

        assert survey.name == "Encuesta Burnout"
        assert survey.status == "Activa"

    def test_survey_response(self):

        survey = SurveyResponse(
            id=uuid.uuid4(),
            name="Encuesta General",
            aperture_date=date.today(),
            finishing_date=date.today(),
            status="Finalizada"
        )

        assert survey.status == "Finalizada"

    def test_question_in_survey(self):

        question = QuestionInSurvey(
            id=uuid.uuid4(),
            text="¿Te sientes agotado?",
            psicometric_variable="Burnout"
        )

        assert question.text == "¿Te sientes agotado?"

    def test_survey_with_questions(self):

        question = QuestionInSurvey(
            id=uuid.uuid4(),
            text="¿Te sientes agotado?",
            psicometric_variable="Burnout"
        )

        survey = SurveyWithQuestions(
            id=uuid.uuid4(),
            name="Encuesta Completa",
            questions=[question]
        )

        assert len(survey.questions) == 1
        assert survey.questions[0].psicometric_variable == "Burnout"