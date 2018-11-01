import os
import json
import hashlib
import zipfile

from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponse

from rest_framework.response import Response
from rest_framework import permissions, exceptions
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication

from problem.serializers import TestCaseUploadForm
from problem.models import Problem
from utils.shortcuts import rand_str, natural_sort_key
from apps.utils.authentication import CsrfExemptSessionAuthentication


class TestCaseView(APIView):
    """Test case view.

Download test case:

    GET /?problem_id=<problem_id>

Upload test case:

    POST / in form-data
    {
        "spj": <boolean>,
        "file": <zip_file>
    }

    Success:
    {
        "data": {
            "hint": null,
            "id": <hash_id>,
            "info": [
                {
                    "input_name": "N.in",
                    "input_size": <input_size>,
                    "output_name": "N.out",
                    "output_size": <output_size>,
                    "stripped_output_md5": "<md5_value>"
                },
                ...
            ],
            "spj": <boolean>,
        },
        "error": null
    }
    """
    # Origin version is on problem.views.admin.TestCaseAPI.
    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, request):
        """Get queryset for users with different permissions."""
        user = request.user
        param = {'visible': True}

        # Regular user has limited access permission.
        if not user.is_admin_role():
            param.update({'courses': None})
        queryset = Problem.objects.filter(**param)

        return queryset

    def filter_name_list(self, name_list, spj):
        ret = []
        prefix = 1
        if spj:
            while True:
                in_name = str(prefix) + ".in"
                if in_name in name_list:
                    ret.append(in_name)
                    prefix += 1
                    continue
                else:
                    return sorted(ret, key=natural_sort_key)
        else:
            while True:
                in_name = str(prefix) + ".in"
                out_name = str(prefix) + ".out"
                if in_name in name_list and out_name in name_list:
                    ret.append(in_name)
                    ret.append(out_name)
                    prefix += 1
                    continue
                else:
                    return sorted(ret, key=natural_sort_key)

    def get(self, request):
        problem_id = request.GET.get("problem_id")
        if not problem_id:
            return Response("Parameter error, problem_id is required")

        queryset = self.get_queryset(request)  # queryset for user.
        try:
            problem = queryset.get(id=problem_id)
        except Problem.DoesNotExist:
            return Response("Problem does not exists")

        # Only admin can download test case of non-public problem.
        user = request.user
        if not user.is_admin_role() and (problem.contest or problem.courses.exists()):
            raise exceptions.PermissionDenied('Permission Denied')

        # if problem.contest:
        #     ensure_created_by(problem.contest, request.user)
        # else:
        #     ensure_created_by(problem, request.user)

        test_case_dir = os.path.join(settings.TEST_CASE_DIR, problem.test_case_id)
        if not os.path.isdir(test_case_dir):
            return self.error("Test case does not exists")
        name_list = self.filter_name_list(os.listdir(test_case_dir), problem.spj)
        name_list.append("info")
        file_name = os.path.join(test_case_dir, problem.test_case_id + ".zip")
        with zipfile.ZipFile(file_name, "w") as file:
            for test_case in name_list:
                file.write(f"{test_case_dir}/{test_case}", test_case)
        if os.environ.get("OJ_ENV") == "production":
            response = HttpResponse()
            response["X-Accel-Redirect"] = file_name
        else:
            response = StreamingHttpResponse(FileWrapper(open(file_name, "rb")),
                                             content_type="application/octet-stream")

        response["Content-Disposition"] = f"attachment; filename=problem_{problem.id}_test_cases.zip"
        response["Content-Length"] = os.path.getsize(file_name)
        return response

    def post(self, request):
        form = TestCaseUploadForm(request.POST, request.FILES)
        if form.is_valid():
            spj = form.cleaned_data["spj"] == "true"
            file = form.cleaned_data["file"]
        else:
            return self.error("Upload failed")
        tmp_file = os.path.join("/tmp", rand_str() + ".zip")
        with open(tmp_file, "wb") as f:
            for chunk in file:
                f.write(chunk)
        try:
            zip_file = zipfile.ZipFile(tmp_file)
        except zipfile.BadZipFile:
            return self.error("Bad zip file")
        name_list = zip_file.namelist()
        test_case_list = self.filter_name_list(name_list, spj=spj)
        if not test_case_list:
            return self.error("Empty file")

        test_case_id = rand_str()
        test_case_dir = os.path.join(settings.TEST_CASE_DIR, test_case_id)
        os.mkdir(test_case_dir)

        size_cache = {}
        md5_cache = {}

        for item in test_case_list:
            with open(os.path.join(test_case_dir, item), "wb") as f:
                content = zip_file.read(item).replace(b"\r\n", b"\n")
                size_cache[item] = len(content)
                if item.endswith(".out"):
                    md5_cache[item] = hashlib.md5(content.rstrip()).hexdigest()
                f.write(content)
        test_case_info = {"spj": spj, "test_cases": {}}

        hint = None
        diff = set(name_list).difference(set(test_case_list))
        if diff:
            hint = ", ".join(diff) + " are ignored"

        ret = []

        if spj:
            for index, item in enumerate(test_case_list):
                data = {"input_name": item, "input_size": size_cache[item]}
                ret.append(data)
                test_case_info["test_cases"][str(index + 1)] = data
        else:
            # ["1.in", "1.out", "2.in", "2.out"] => [("1.in", "1.out"), ("2.in", "2.out")]
            test_case_list = zip(*[test_case_list[i::2] for i in range(2)])
            for index, item in enumerate(test_case_list):
                data = {"stripped_output_md5": md5_cache[item[1]],
                        "input_size": size_cache[item[0]],
                        "output_size": size_cache[item[1]],
                        "input_name": item[0],
                        "output_name": item[1]}
                ret.append(data)
                test_case_info["test_cases"][str(index + 1)] = data

        with open(os.path.join(test_case_dir, "info"), "w", encoding="utf-8") as f:
            f.write(json.dumps(test_case_info, indent=4))

        return Response({
            'error': None,
            'data': {"id": test_case_id, "info": ret, "hint": hint, "spj": spj},
        })
