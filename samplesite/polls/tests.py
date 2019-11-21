import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns for questions whose pub_date is in the future.
        :return:
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """old date"""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_recently_question(self):
        """recently date"""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), True)


def create_question(question_text: str, days: int):
    """テスト用質問生成メソッド"""
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """質問なしコメント出力"""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """公開済み質問1件あり"""
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past question.>'])

    def test_future_question(self):
        """公開前質問1件あり"""
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """公開前質問1件、公開後質問1件あり"""
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past question.>'])

    def test_two_past_questions(self):
        """公開後質問2件あり"""
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past question 2.>',
                                  '<Question: Past question 1.>', ])


class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        """公開前の詳細情報は表示しない"""
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse('polls:detail', args=(future_question.id, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """公開後の詳細情報は表示する"""
        past_question = create_question(question_text="Past question.", days=-5)
        url = reverse('polls:detail', args=(past_question.id, ))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
