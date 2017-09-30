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
   
def RunUserProcess(user, command):
    payload = { 'command': command }
    headers = { 'content-type': 'application/json' }
    r = requests.post(
        "http://%s" % settings.IMPERSONATOR['endpoint'], 
        data=json.dumps(payload),
        headers=headers
    )
    return r.json()['out']


    
def CreateTempDir(username):
    tmp_dir = os.path.join(settings.TEMP_DIR, "." + username)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
        os.chmod(tmp_dir, 0777)
    return tmp_dir
    
    

def ACLResponse(response):
    if response.startswith("ERROR:"):
        #remove the first 3 lines and convert to html by replacing newlines with <br/> and removing return carriages
        response = '<br/>'.join(response.split('\n')[2:]).replace('\r', '') 
        return Response(response, status=400)
    else:
        return Response(response)  
    


def GetFileStat(user, path):
    statinfo = RunUserProcess(user, "%s '%s/manage.py' acl STAT %s" % (settings.PYTHON_VENV, PROJECT_PATH, path)).split()
    return statinfo


#Views    
   
class DirectoryDetail(APIView):
    permission_classes = (IsAuthenticated,)
        
    def get(self, request):
        """
        Get directory path and listing details for given path
        """           
        path = request.GET.get("path", os.path.abspath(os.path.sep))
        out = RunUserProcess(request.user, "%s '%s/manage.py' acl GET_DIR '%s'" % (settings.PYTHON_VENV, PROJECT_PATH, path))
        return ACLResponse(out) 
            
            
  
class Operation(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, op):
        """
        Create file or directory
        """
        try:
            out = RunUserProcess(request.user, "%s '%s/manage.py' acl CREATE '%s' '%s' %s" % (settings.PYTHON_VENV, PROJECT_PATH, request.POST["name"], request.POST["fullpath"], request.POST["type"]))
            return ACLResponse(out)
        
        except Exception, ex:
            return Response(str(ex), status=400) 
        
    
    def put(self, request, op):
        """
        Perform a rename, move, or copy operation on a file or directory
        """
        try:
            dir_dict = lambda:None
            dir_dict.__dict__ = json.loads(request.body)
            
            op = op.upper()
            cmd = "%s '%s/manage.py' acl %s '%s' '%s' %s" % (settings.PYTHON_VENV, PROJECT_PATH, op, dir_dict.name, dir_dict.fullpath, dir_dict.type)
            
            if op != "RENAME":
                cmd += " %s" % dir_dict.destination
            
            out = RunUserProcess(request.user, cmd)
            
            return ACLResponse(out)
        except Exception, ex:
            return Response(str(ex), status=400)
        
        
    
    def delete(self, request, op):
        """
        Delete file or directory
        """       
        try:
            delete = QueryDict(request.body)
            cmd = "%s '%s/manage.py' acl DELETE '%s' '%s' %s" % (settings.PYTHON_VENV, PROJECT_PATH, delete["name"], delete["fullpath"], delete["type"])
            out = RunUserProcess(request.user, cmd)
            
            return ACLResponse(out)
        except Exception, ex:
            return Response(str(ex), status=400)         


    
class FileDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def delete(self, request):
        """
        Delete tab at a given path
        """
        try:  
            filepath = request.GET.get("path", os.path.abspath(os.path.sep))
            
            tab, created = Tab.objects.get_or_create(User=request.user, FilePath=filepath)
            tab.delete()
            
            return Response()
        except Exception, ex:
            return Response("", status=400)
    
    
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
            type = mimetypes.types_map.get(file_ext.lower(), "text/plain")
            if type == "application/javascript":
                type = "text/plain"
            
            if request.method == "HEAD":
                response = HttpResponse("", content_type=type)
                return response
            else:
                tmp_dir = CreateTempDir(request.user.username)
                
                cmd = "%s '%s/manage.py' acl CREATE_TEMP_FILE '%s' '%s'" % (settings.PYTHON_VENV, PROJECT_PATH, filepath, os.path.join(tmp_dir, os.path.basename(filepath)))  
                out = RunUserProcess(request.user, cmd)
                
                tmp_file = out.strip().strip("\r").strip("\n") 
                
                #create Tab
                last_saved = 'n/a'
                try:
                    tab, created = Tab.objects.get_or_create(User=request.user, FilePath=filepath)
                    tab.save()
                except Exception, err:
                    with open("/tmp/tab.log","w") as f:
                        print >> f, str(err)
                
                if not out.startswith("ERROR:\n\n"):                     
                    wrapper = FileWrapper(open(tmp_file, "rb"))
                    response = HttpResponse(wrapper, content_type=type)
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
            
            tmp_dir = CreateTempDir(request.user.username)
            
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
            out = RunUserProcess(request.user, cmd)
            
            if not out.startswith("ERROR:\n\n"):
                #update Tab LastSaved date
                try:
                    statinfo = GetFileStat(request.user, path)
                    
                    tab, created = Tab.objects.get_or_create(User=request.user, FilePath=path)
                    tab.LastSaved = int(statinfo[8])
                    tab.save()
                        
                    out = str(tab.LastSaved)
                except Exception, ex:
                    out = "ERROR:\n\nTab not saved: %s" % str(ex)
            
            return ACLResponse(out)
                
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
                          
            tmp_dir = CreateTempDir(request.user.username)
            
            cmd = "%s '%s/manage.py' acl CREATE_TEMP_FILE '%s' '%s'" % (settings.PYTHON_VENV, PROJECT_PATH, filepath, os.path.join(tmp_dir, os.path.basename(filepath)))          
            out = RunUserProcess(request.user, cmd)
            
            tmp_file = out.strip().strip("\\r").strip("\r").strip("\n")              
            
            if not out.startswith("ERROR:\n\n"):                     
                wrapper = FileWrapper(open(tmp_file, "rb"))
                response = HttpResponse(wrapper, content_type='application/force-download')
                response['Content-Length'] = os.path.getsize(tmp_file)
                response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filepath)
                return response
            else:
                return Response(out, status=400)
        
        except Exception, ex:
            return Response(str(ex), status=400) 
            
    
    def post(self, request):
        """
        Upload files to given path
        """ 
        try:       
            path = request.POST["path"]
                          
            tmp_dir = CreateTempDir(request.user.username)
            
            output = ""
            
            for f in request.FILES.getlist("files"):
                tmp_path = os.path.join(tmp_dir, f.name)
                
                #upload each file to a temporary location
                with open(tmp_path, 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                os.chmod(tmp_path, 0775)
                
                #move from temporary location to new location
                cmd = "%s '%s/manage.py' acl MOVE '%s' '%s' %s '%s'" % (settings.PYTHON_VENV, PROJECT_PATH, f.name, tmp_path, 'file', path)
                out = RunUserProcess(request.user, cmd)
                
                #append any errors that occur to output
                if out.startswith("ERROR:\n\n"):
                    output += "%s\n\n" % out
            
            return ACLResponse(output);
        
        except Exception, ex:
            return Response(str(ex), status=400) 


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
            return Response(str(ex), status=400)


class Tabs(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        tabs = Tab.objects.filter(User=request.user)
        serializer = TabListSerializer(tabs, many=True)
        return Response(serializer.data)
    
