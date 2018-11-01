problem_viewset = """
# Create
Create problem:

    POST /
    {
      # The following is added for DGUTOJ.
      "collection": <collection_id>,
      "course": <course_id>,
      "contest": <contest_id>,  # Not required.

      "_id": <display_id>,
      "title": "<title>",
      "description": "<description>",
      "input_description": "<input_description>",
      "output_description": "<output_description>",
      "time_limit": <time_limit_in_millisecond>, # default is 1000
      "memory_limit": <memory_limit_in_MB>, # default is 256
      "difficulty": "<Low, Mid or High>",
      "visible": <boolean>,
      "tags": [
        "<tag1_name>",
        "<tag2_name>",
        ...
      ],
      "languages": [
        "C",
        "C++",
        "Java",
        "Python2",
        "Python3"
      ],
      "template": null,
      "samples": [
        {
          "input": "<sample_input>",
          "output": "<sample_output>"
        },
        {
          "input": "<sample_input>",
          "output": "<sample_output>"
        }
      ],
      "spj": <boolean>,
      "spj_language": "C",
      "spj_code": "",
      "spj_compile_ok": false,
      "test_case_id": "<test_case_id>",
      "test_case_score": [
        {
          "stripped_output_md5": "<stripped_output_md5>",
          "input_size": <input_size_in_bytes>,
          "output_size": <output_size_in_bytes>,
          "input_name": "<input_file>",
          "output_name": "<output_file>",
          "score": "<score>"
        }
      ],
      "rule_type": "<ACM or OI>",
      "hint": "<hint>",
      "source": "<source>"
    }

Whether a user can create a problem.

Regular user can only create a problem if she haven't run out of her
invalid problems quota.

`GET /<problem_id>/can_create/`

# Vote
Vote problem:

    POST /<problem_id>/vote/
    {
      "is_up": <Boolean>
    }

Get user vote status of a problem:

    GET /<problem_id>/

    {
      ...
      "vote_status": <status_code>
    }

    ---
    Vote status code:
    0 means user have not voted.
    1 means user voted up.
    2 means user voted down.

# Validate

    PUT /<problem_id>/validate/
    {}

# Comment

List comments of a problem: `GET /<problem_id>/comments/`

Post a comment to a problem.

    POST /<problem_id>/comment/
    {
        "content": <comment_content>
    }

# Move Course Problems To Public
Move a course problem to public problem set with a collection you
choose.

    POST /<id>/move_public/
    {
        "collection": <id>
    }

Move all problems of a course to public problem set with a default
collection you choose.

    POST /batch_move_public/
    {
        "collection": <id>,
        "course": <id>
    }

# Pick One
Pick a random problem for user.

    GET /pick_one/


# Delegatian
Course problems created by my delegates. 

    GET /my_delegation/


# Filter
Filter problems of a contest: `GET /?contest_id=<contest_id>`

Filter problems not in contest: `GET /?contest_id=0`

Filter problems in course: `GET /?in_course=true`

Filter problems in descended order of up votes: `GET /?vote_rank=1`

Filter problems in descended order of down votes: `GET /?vote_rank=-1`

Filter problems which user has permission to change: `GET /?has_perm=true`

Filter problems of a course: `/?course_id=<course_id>`

Filter problems of a collection: `/?collection_id=<collection_id>`
"""
