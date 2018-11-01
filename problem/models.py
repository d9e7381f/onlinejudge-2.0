from math import sqrt

from django.conf import settings
from django.db import models
from django.db.models import Sum
from utils.models import JSONField

from account.models import User, UserProfile
from contest.models import Contest
from utils.models import RichTextField
from utils.constants import Choices


class ProblemTag(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        db_table = "problem_tag"


class ProblemRuleType(Choices):
    ACM = "ACM"
    OI = "OI"


class ProblemDifficulty(object):
    High = "High"
    Mid = "Mid"
    Low = "Low"


class Problem(models.Model):
    # display ID
    _id = models.CharField(max_length=24, db_index=True)
    contest = models.ForeignKey(Contest, null=True, blank=True)
    # for contest problem
    is_public = models.BooleanField(default=False)
    title = models.CharField(max_length=128)
    # HTML
    description = RichTextField()
    input_description = RichTextField()
    output_description = RichTextField()
    # [{input: "test", output: "123"}, {input: "test123", output: "456"}]
    samples = JSONField()
    test_case_id = models.CharField(max_length=32)
    # [{"input_name": "1.in", "output_name": "1.out", "score": 0}]
    test_case_score = JSONField()
    hint = RichTextField(blank=True, null=True)
    languages = JSONField()
    template = JSONField()
    create_time = models.DateTimeField(auto_now_add=True)
    # we can not use auto_now here
    last_update_time = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User)
    # ms
    time_limit = models.IntegerField()
    # MB
    memory_limit = models.IntegerField()
    # special judge related
    spj = models.BooleanField(default=False)
    spj_language = models.CharField(max_length=32, blank=True, null=True)
    spj_code = models.TextField(blank=True, null=True)
    spj_version = models.CharField(max_length=32, blank=True, null=True)
    spj_compile_ok = models.BooleanField(default=False)
    rule_type = models.CharField(max_length=32)
    visible = models.BooleanField(default=True)
    difficulty = models.CharField(max_length=32)
    tags = models.ManyToManyField(ProblemTag)
    source = models.CharField(max_length=200, blank=True, null=True)
    # for OI mode
    total_score = models.IntegerField(default=0, blank=True)
    submission_number = models.BigIntegerField(default=0)
    accepted_number = models.BigIntegerField(default=0)
    # {JudgeStatus.ACCEPTED: 3, JudgeStaus.WRONG_ANSWER: 11}, the number means count
    statistic_info = JSONField(default=dict)
    vote_rank_score = models.FloatField(default=0.0)  # Score of vote rank.
    is_open_test_case = models.BooleanField('测试用例公开的题目', default=False)
    is_valid = models.BooleanField('有效题目', default=False)

    class Meta:
        db_table = "problem"
        unique_together = (("_id", "contest"),)
        ordering = ("create_time",)

    def add_submission_number(self):
        self.submission_number = models.F("submission_number") + 1
        self.save(update_fields=["submission_number"])

    def add_ac_number(self):
        self.accepted_number = models.F("accepted_number") + 1
        self.save(update_fields=["accepted_number"])

    @property
    def vote_up_count(self):
        return self.votes.filter(is_up=True).count()

    @property
    def vote_down_count(self):
        return self.votes.filter(is_up=False).count()

    def vote_score(self):
        """Get sum of vote score of problem."""
        return self.votes.aggregate(score=Sum('score'))['score'] or 0

    def vote_trigger(self):
        """
        Trigger to validate or delete a problem base on its votes.
        """
        vote_score = self.vote_score()
        if not self.is_valid:
            # When a problem's vote count exceed N and it's still
            # invalid, validate it if up count is more than down count,
            # otherwise delete it.
            if self.votes.count() > settings.MAX_VOTES_BEFORE_TRIGGER:
                if self.votes.filter(is_up=True).count() \
                   > self.votes.filter(is_up=False).count():
                    self.is_valid = True
                    self.save()
                else:
                    self.delete()

            # Delete it when its score less than equal X.
            elif vote_score <= settings.VOTE_SCORE_INVALID_TO_DELETE:
                self.delete()

            # Validate it when its score larger than equal X.
            elif vote_score >= settings.VOTE_SCORE_INVALID_TO_VALID:
                self.is_valid = True
                self.save()

        # Delete a valid one when its score less than equal X.
        elif vote_score <= settings.VOTE_SCORE_VALID_TO_DELETE:
            self.delete()

    def update_user_status(self):
        """Update user submission statistic info."""
        from submission.models import JudgeStatus

        # Get the user submission number, and best or latest submission
        # result.
        # If user had solved the problem, result code would be
        # ACCEPTED, otherwise would be the latest result.
        queryset = self.submission_set.raw("""
        select distinct on (user_id)
               *, count(*) over (partition by user_id) as submission_number
        from submission
        where problem_id=%s
        order by user_id
        ,case when result=0 then 0 else 1 end
        ,create_time desc
        limit 1""", [self.pk])

        for submission in queryset:
            userprofile = UserProfile.objects.get(user_id=submission.user_id)
            userprofile.submission_number += submission.submission_number

            if self.rule_type == 'ACM':
                if submission.result == JudgeStatus.ACCEPTED:
                    userprofile.accepted_number += 1

                info = userprofile.acm_problems_status
                info['problems'][str(self.pk)]['status'] = submission.result
                userprofile.acm_problems_status = info
            else:
                # OI rule.
                pass

            userprofile.save()

    def update_vote_rank_score(self):
        """Update vote rank score.

        How Not To Sort By Average Rating – Evan Miller
        http://www.evanmiller.org/how-not-to-sort-by-average-rating.html
        """
        if not self.votes.exists():
            self.vote_rank_score = 0
        else:
            n = self.votes.count()
            p = self.votes.filter(is_up=True).count() / n
            z = settings.VOTE_RANK_Z_SCORE
            self.vote_rank_score = (p + z**2/(2*n) - z*sqrt((p*(1-p)+z**2/(4*n))/n)) / (1+z**2/n)
            self.save()
