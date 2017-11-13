# UrlGrabber
Url grabber for .NET projects

# Overview
This script is used to find the URLs in the source code of the web applications on the .net platform. This script is still on the  development stage. The functional will be improved / extended further.

***URL grabbing is performed based on standard .NET routing conventions:***
1. Presence the [Route] attribute on MVC actions.
2. Presence the [RoutePrefix] attribute on the controllers.
3. Basic {controller}/{action}/{id} rules.
4. If the WebApiConfig.cs is present, its content is taking into account.

# Features
1. Find URLs
2. Determining of the HTTP method for each URL
3. Determining of the prameters for each URL

# How to use
1. `git clone https://github.com/Mike-n1/UrlGrabber`
2. `cd UrlGrabber`
3. `python Url_Grabber.py -d SOURCE_CODE_FOLDER`
