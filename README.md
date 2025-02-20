<div align="center">

<h1>Image To Ready</h1>
This service randomly selects 5 images from a collection, prepares them either as a slideshow video or in their original form, and uploads them to the web.<br/><br/>

<picture><img src="https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=FFFFFF" alt="..."></picture>
<picture><img src="https://img.shields.io/badge/-Python3-3776AB?style=flat-square&logo=python&logoColor=FFFFFF" alt="..."></picture>
<picture><img src="https://img.shields.io/badge/-Rclone-3F79AD?style=flat-square&logo=rclone&logoColor=FFFFFF" alt="..."></picture>
<picture><img src="https://img.shields.io/badge/FFMPEG-007808?style=flat-square&logo=ffmpeg&logoColor=FFFFFF" alt="..."></picture>

</div>

## Acknowledgment

This service was developed with the help of Vrchat users [5ignal](https://github.com/5ignal) and [applemint231](https://github.com/applemint231).

<div align="center">

</div>

## Demo

<div align="center">



</div>

## Description

It supports two options: using rclone and utilizing a local storage solution.

## Function

- Output results using SFTP
- Reference external storage using rclone
- Reference using local storage
- An algorithm that prevents conflicts with previous selections when randomly choosing from the

## Install

Select either directory 2 or directory 3 and apply it to the ```RUN git clone``` command in the Dockerfile. After that, modify the ```png2mp4.json``` file. Below is an example:

```

{
    "interTime" : 5,

    "locale_inp" : "/source",
    "locale_blacklist" : ["_JustDance"],

    "locale_tag" : {

        "mado": "MD",
        "__ELSE__" : "NB"
    },

    "tag_on" : true,
    "date_type" : 2,
    "mp4_on" : false,

    "drop" : {
        "distance" : 5,
        "step" : 600
    },

    "sftp" : {
        "host" : "111.111.111.111", 
        "port" : 12000,
        "id" : "root",
        "pw" : "!!!!1!!!!", 
        "locale" : "/usr/share/nginx/html/"
    },
    "cmd" : [
        "rclone mount remote:/_Share/_Lock/VRC /source --read-only --daemon --vfs-cache-mode full --vfs-cache-max-size 20G"
    ],

    "jd" : {
        "sw" : true,
        "inp" : "/source/_JustDance",
        "blacklist" : ["@eaDir"], 
        "distance" : 1,
        "step" : 2
    }
}

```
