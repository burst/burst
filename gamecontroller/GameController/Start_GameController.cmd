@echo off
set /P blue=Enter team number for blue: 
set /P red=Enter team number for red: 
set broadcast=

echo Starting GameController, team %blue% plays in blue and team %red% plays in red

if %1x == x goto label
set broadcast=-broadcast %1
echo Broadcasting into network %1
:label

java -jar GameController.jar %broadcast% -numplayers 3 %blue% %red%
