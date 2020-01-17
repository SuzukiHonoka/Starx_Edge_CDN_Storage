# Starx_Edge_CDN_Storage
A self-host simple static cdn storage.

## How does it work?

It rewrites the 404 error handler of `Flask`.  
When someone trying to access a URL which is no route.  
It'll to decide the path of URL is secure or not?  
Then trying to find whether local static folder has that file.  
If not,respone with 302 to orinal path.  
And at the same time,  
It'll start a download thread for download that file.  
And next time someone trying to access that path,  
The app will dirct send that local file to client.  
So the work is simple.  

It also provides a info page of status.

## Performance
This is a non-test version.  
PLEASE DO NOT USE IT TO PRODUCE ENV.

## Safety

I have added some simple URL filter at URL check,  
But it is a very simple one.  
Use it as your own risk.

## Get Started

PLEASE DON NOT USE `flask run` in your ENV.  
This is just a built-in function for debug only!  
Better use a wsgi server software like `Gunicorn`.

## Recommand Composition

I use `NGINX + Gunicorn` as my way.
But you can decide as your want.

## Demo

Demo1: [Click here for visit](https://cdn3.ioflow.xyz "Demo1")

## End

My blog: [Starx's Home](https://www.ioflow.xyz "Starx's Home")

If you like my work please give me a star and follow me.  
Thanks for you support!

That's it!
