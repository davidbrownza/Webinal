from django.shortcuts import render
from django.http import HttpResponse, Http404, QueryDict
from wsgiref.util import FileWrapper
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import os, json, mimetypes, platform, shutil, traceback, requests, datetime

from models import *
from objects import *
from serializers import *

from utilities.security.cryptography import PubPvtKey

#Global variables and functions
PROJECT_PATH = settings.BASE_DIR

def run_process(user, command):
    payload = { 'token': user.Credentials.Token, 'command': command }
    headers = { 'content-type': 'application/json' }

    response = requests.post(
        "http://%s" % settings.IMPERSONATOR['endpoint'],
        data=json.dumps(payload),
        headers=headers
    ).json()

    return response['out'], response['err'], response['code']

def get_response(out, err, code):
    response, status = (out, 200) if code == 0 else (err, 500)
    return Response(response, status=status)


def create_tmp_dir(username):
    tmp_dir = os.path.join(settings.TEMP_DIR, "." + username)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
        os.chmod(tmp_dir, 0777)
    return tmp_dir


def get_file_stat_info(user, path):
    command = "%s '%s/manage.py' acl STAT %s" % (settings.PYTHON_VENV, PROJECT_PATH, path)
    statinfo = run_process(user, command).split()
    return statinfo


#Views

class DirectoryDetail(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Get directory path and listing details for given path
        """
        path = request.GET.get("path", os.path.abspath(os.path.sep))
        out, err, code = run_process(request.user, "%s '%s/manage.py' acl GET_DIR '%s'" % (settings.PYTHON_VENV, PROJECT_PATH, path))

        return get_response(out, err, code)



class Operation(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, op):
        """
        Create file or directory
        """
        out, err, code = run_process(request.user, "%s '%s/manage.py' acl CREATE '%s' '%s' %s" % (settings.PYTHON_VENV, PROJECT_PATH, request.POST["name"], request.POST["fullpath"], request.POST["type"]))
        return get_response(out, err, code)


    def put(self, request, op):
        """
        Perform a rename, move, or copy operation on a file or directory
        """
        dir_dict = lambda:None
        dir_dict.__dict__ = json.loads(request.body)

        op = op.upper()
        cmd = "%s '%s/manage.py' acl %s '%s' '%s' %s" % (settings.PYTHON_VENV, PROJECT_PATH, op, dir_dict.name, dir_dict.fullpath, dir_dict.type)

        if op != "RENAME":
            cmd += " %s" % dir_dict.destination

        out, err, code = run_process(request.user, cmd)
        return get_response(out, err, code)



    def delete(self, request, op):
        """
        Delete file or directory
        """
        delete = QueryDict(request.body)
        cmd = "%s '%s/manage.py' acl DELETE '%s' '%s' %s" % (settings.PYTHON_VENV, PROJECT_PATH, delete["name"], delete["fullpath"], delete["type"])
        out, err, code = run_process(request.user, cmd)
        return get_response(out, err, code)



class FileDetail(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        """
        Delete tab at a given path
        """
        filepath = request.GET.get("path", os.path.abspath(os.path.sep))

        tab, created = Tab.objects.get_or_create(User=request.user, FilePath=filepath)
        tab.delete()

        return Response()


    def get(self, request):
        """
        Fetch file located at a given path. This is done by creating a temporary
        file that is accessible by the web server and then returning the
        temporary file.
        """
        try:
            filepath = request.GET.get("path", os.path.abspath(os.path.sep))

            #Get file type
            mimetypes.init()
            name, file_ext = os.path.splitext(os.path.basename(filepath))
            content_type = mimetypes.types_map.get(file_ext.lower(), "text/plain")
            if content_type.endswith("javascript"):
                content_type = "text/plain"

            if request.method == "HEAD":
                response = HttpResponse("", content_type=content_type)
                return response
            else:
                tmp_dir = create_tmp_dir(request.user.username)

                cmd = "%s '%s/manage.py' acl CREATE_TEMP_FILE '%s' '%s'" % (settings.PYTHON_VENV, PROJECT_PATH, filepath, os.path.join(tmp_dir, os.path.basename(filepath)))
                out, err, code = run_process(request.user, cmd)

                tmp_file = out.strip().strip("\r").strip("\n")

                #create Tab
                last_saved = 'n/a'
                try:
                    tab, created = Tab.objects.get_or_create(User=request.user, FilePath=filepath)
                    tab.save()
                except Exception, err:
                    with open("/tmp/tab.log","w") as f:
                        print >> f, str(err)

                if code == 0:
                    wrapper = FileWrapper(open(tmp_file, "rb"))
                    response = HttpResponse(wrapper, content_type=content_type)
                    response['File-Modified'] = last_saved
                    response['Content-Length'] = os.path.getsize(tmp_file)
                    return response
                else:
                    return Response(out, status=400)
        except Exception, err:
            return Response(str(err), status=400)


    def post(self, request):
        """
        Save a text file to the given path with the given contents
        """
        try:
            path = request.POST["path"]
            contents = request.POST["contents"]

            tmp_dir = create_tmp_dir(request.user.username)

            #determine path to temp file
            temp = os.path.join(tmp_dir, os.path.basename(path)) + ".tmp."
            num = 0
            while os.path.exists(temp + str(num)):
                num += 1
            temp = temp + str(num)

            #create temp file
            with open(temp, 'w') as f:
                f.write(contents.encode('utf-8'))

            cmd = "%s '%s/manage.py' acl OVERWRITE_FILE '%s' '%s'" % (settings.PYTHON_VENV, PROJECT_PATH, path, temp)
            out, err, code = run_process(request.user, cmd)

            if code == 0:
                #update Tab LastSaved date
                try:
                    statinfo = get_file_stat_info(request.user, path)

                    tab, created = Tab.objects.get_or_create(User=request.user, FilePath=path)
                    tab.LastSaved = int(statinfo[8])
                    tab.save()

                    out = str(tab.LastSaved)
                except Exception, ex:
                    err = "ERROR:\n\nTab not saved: %s" % str(ex)
                    code = -1

            return get_response(out, err, code)

        except Exception, ex:
            return Response(traceback.format_exc(), status=400)


class FileTransfer(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Download file located at a given path
        """
        try:
            filepath = request.GET.get("path", os.path.abspath(os.path.sep))

            tmp_dir = create_tmp_dir(request.user.username)

            cmd = "%s '%s/manage.py' acl CREATE_TEMP_FILE '%s' '%s'" % (settings.PYTHON_VENV, PROJECT_PATH, filepath, os.path.join(tmp_dir, os.path.basename(filepath)))
            out, err, code = run_process(request.user, cmd)

            tmp_file = out.strip().strip("\\r").strip("\r").strip("\n")

            if code == 0:
                wrapper = FileWrapper(open(tmp_file, "rb"))
                response = HttpResponse(wrapper, content_type='application/force-download')
                response['Content-Length'] = os.path.getsize(tmp_file)
                response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filepath)
                return response
            else:
                return get_response(out, err, code)

        except Exception, ex:
            return Response(str(ex), status=500)


    def post(self, request):
        """
        Upload files to given path
        """
        try:
            path = request.POST["path"]

            tmp_dir = create_tmp_dir(request.user.username)

            error = ""

            for f in request.FILES.getlist("files"):
                tmp_path = os.path.join(tmp_dir, f.name)

                #upload each file to a temporary location
                with open(tmp_path, 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                os.chmod(tmp_path, 0775)

                #move from temporary location to new location
                cmd = "%s '%s/manage.py' acl MOVE '%s' '%s' %s '%s'" % (settings.PYTHON_VENV, PROJECT_PATH, f.name, tmp_path, 'file', path)
                out, err, code = run_process(request.user, cmd)

                #append any errors that occur to output
                if code != 0:
                    error += "%s\n\n" % err

            return Response(error)

        except Exception, ex:
            return Response(str(ex), status=500)


class SettingsDetail(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Get user settings for file manager
        """
        try:
            settings = FileManagerSettings.objects.get(User=request.user)
            data = Settings(settings.HomeDirectory, settings.AceTheme, settings.FontSize)
            return Response(data.to_JSON())
        except Exception, ex:
            return Response(str(ex), status=400)


    def post(self, request):
        """
        Set user settings for file manager
        """
        try:
            home_directory = request.POST["home_directory"]
            theme = request.POST["theme"]
            font_size = request.POST["font_size"]

            settings = FileManagerSettings.objects.get(User=request.user)
            settings.HomeDirectory = home_directory
            settings.AceTheme = theme
            settings.FontSize = font_size
            settings.save()

            return Response()
        except Exception, ex:
            return Response(str(ex), status=500)


class Tabs(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        tabs = Tab.objects.filter(User=request.user)
        serializer = TabListSerializer(tabs, many=True)
        return Response(serializer.data)

