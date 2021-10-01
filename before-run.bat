@echo off

setlocal enabledelayedexpansion

goto movie

:movie
start "" "pre_dir\vlc\VLCPortable.exe" --loop --fullscreen "movie_address"

