from datetime import datetime
from django.test import TestCase
from PortfolioUser.models import PortfolioUser
from Course.models import Course, CourseUserRelation, CourseChallengeRelation
from Challenge.models import Challenge
from Review.models import Review
from ReviewQuestion.models import ReviewQuestion
from Elaboration.models import Elaboration


class SimpleTest(TestCase):
    def setUp(self):
        self.create_test_users(4)
        self.create_course()
        self.create_challenge()
        self.create_review_question()
        self.create_elaborations()

    def create_test_user(self, username):
        user = PortfolioUser(username=username)
        user.email = '%s@student.tuwien.ac.at.' % username
        user.first_name = 'Firstname_%s' % username
        user.last_name = 'Lastname_%s' % username
        user.nickname = 'Nickname_%s' % username
        user.is_staff = False
        user.is_superuser = False
        password = username
        user.set_password(password)
        user.save()
        return user

    def create_test_users(self, amount):
        print("create test users")
        self.users = []
        for i in range(amount):
            self.users.append(self.create_test_user("s%s" % i))

    def create_course(self):
        print("create test course")
        self.course = Course(
            title='test_title',
            short_title='test_short_title',
            description='test_description',
            course_number='test_course_number',
        )
        self.course.save()
        for user in self.users:
            CourseUserRelation(course=self.course, user=user).save()

    def create_challenge(self):
        print("create test challenge")
        self.challenge = Challenge(
            title='test_title',
            subtitle='test_subtitle',
            description='test_description',
        )
        self.challenge.save()
        CourseChallengeRelation(course=self.course, challenge=self.challenge).save()

    def create_review_question(self):
        print("create test review question")
        self.review_question = ReviewQuestion(
            challenge=self.challenge,
            order=1,
            text="Can you find any additional material not included in this submission?"
        )
        self.review_question.save()

    def create_elaborations(self):
        print("create test elaborations")
        self.elaborations = []
        for user in self.users:
            elaboration = Elaboration(challenge=self.challenge, user=user, elaboration_text="test_text",
                                      submission_time=datetime.now())
            elaboration.save()
            self.elaborations.append(elaboration)

    def create_review_without_submission_date(self, elaboration, reviewer):
        Review(elaboration=elaboration, reviewer=reviewer, appraisal='S').save()

    def create_review(self, elaboration, reviewer):
        Review(elaboration=elaboration, reviewer=reviewer, submission_time=datetime.now(), appraisal='S').save()

    def test_get_open_review(self):
        user1 = self.users[0]
        user2 = self.users[2]
        elaboration = self.elaborations[0]
        self.create_review_without_submission_date(elaboration=elaboration, reviewer=user1)

        # there should be an open review for user1
        review = Review.get_open_review(self.challenge, user1)
        assert review
        assert review.reviewer == user1
        assert review.elaboration == elaboration

        # there should be no open review for user1 since the review is already submitted
        review.submission_time = datetime.now()
        review.save()
        review = Review.get_open_review(self.challenge, user1)
        assert not review

        # there should be no open review for user2
        review = Review.get_open_review(self.challenge, user2)
        assert not review

        # user1 and user2 both have separate open reviews
        self.create_review_without_submission_date(elaboration=elaboration, reviewer=user1)
        self.create_review_without_submission_date(elaboration=elaboration, reviewer=user2)
        review1 = Review.get_open_review(self.challenge, user1)
        review2 = Review.get_open_review(self.challenge, user2)
        assert review1
        assert review2
        assert review1.id != review2.id
        assert review1.reviewer == user1
        assert review2.reviewer == user2
        assert review1.elaboration == elaboration and review2.elaboration == elaboration

    def test_get_review_amount(self):
        for elaboration in self.elaborations:
            i = 0
            for user in self.users:
                i += 1
                self.create_review(elaboration=elaboration, reviewer=user)
                review_amount = Review.get_review_amount(elaboration)
                # each iteration, the amount of reviews should be + 1
                assert review_amount == i

    # TODO: enable this test if we decide that the review amount only counts submitted reviews
    def get_review_amount_without_submission(self):
        for elaboration in self.elaborations:
            for user in self.users:
                self.create_review_without_submission_date(elaboration=elaboration, reviewer=user)
                review_amount = Review.get_review_amount(elaboration)
                # the review amount should not increase without submission_time
                assert review_amount == 0