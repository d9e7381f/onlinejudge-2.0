# from collections import OrderedDict


# please set your own SECRET_KEY to a long random string
# SECRET_KEY = ""

# Validate or delete problem base on votes count.
# VOTE_SCORE_INVALID_TO_VALID = <int>
# VOTE_SCORE_INVALID_TO_DELETE = <nagative int>
# VOTE_SCORE_VALID_TO_DELETE = <nagative int>
# MAX_VOTES_BEFORE_TRIGGER = <int>

# Dynamically update difficulty of problem.
# DIFFICULTY_BASE_SUBMISSIONS_COUNT = <int>
# DIFFICULTY_RATE_MAP = OrderedDict({
#     'Low': <float less than equal 1>,
#     'Mid': <float less than equal 1><,
#     'High': <float less than equal 1>,
# })

# Regular user can only create a problem if she haven't run out of her
# invalid problems quota.
# INVALID_PROBLEMS_QUOTA = <int>

# Authentication for DGUT
# OJ_DOMAIN = ''
# APP_ID = ''
# DGUT_LOGIN = ''
# DGUT_CHECK_TOKEN = ''
# DGUT_LOGOUT = ''
# DGUT_USER_INFO = ''
# DGUT_APP_SECRET = ''

# Vote Rank Algorithm
# Use 1.96 for a confidence level of 0.95.
# VOTE_RANK_Z_SCORE = 1.96
