@echo off&setlocal enabledelayedexpansion
color 3b
mode con:cols=41 lines=8
title ⑥【剧场版：伦敦】  ◎制作：Cyxgg
if not exist "%temp%\dep" md "%temp%\dep"
if not exist "%temp%\dep\ctime.ini" echo.2>"%temp%\dep\ctime.ini"
if not exist "%temp%\dep\play.ini" echo %cd%\play.mp3>"%temp%\dep\play.ini"
mplayer/? >nul 2>nul||call :msg 缺失文件：mplayer.exe，压缩包可能未解压，请解压后使用。 16 Edgar博士の谜：错误信息&&exit
choice/?>nul 2>nul||call :msg 缺失文件：choice.exe，压缩包可能未解压，请解压后使用。 16 Edgar博士の谜：错误信息&&exit
wj||call :msg 缺失文件：wj.exe，可能被杀软误杀，请将其加入白名单。 16 Edgar博士の谜：错误信息&&exit
cmos >nul||call :msg 缺失文件：cmos.exe，可能被杀软误杀，请将其加入白名单。 16 Edgar博士の谜：错误信息&&exit
del *.物品>nul 2>nul
set /a ju=(3+%random%%%7)*1000
set /a dg=(30+%random%%%70)*100
set /a s=(30+%random%%%70)*10
set 烤地瓜=0
set dg1=0
for /f "delims=:. tokens=1,2,3" %%a in ('echo.%time%') do (set shi=%%a&set fen=%%b&set miao=%%c)
set /p ctime=<"%temp%\dep\ctime.ini"
set /p play=<"%temp%\dep\play.ini"
::if not exist 片头.rmvb call :msg 缺失片头文件，压缩包可能未解压，请解压后使用。 16 Edgar博士の谜：错误信息&&exit
::if not exist play.mp3 call :msg 缺失音乐文件，压缩包可能未解压，请解压后使用。 16 Edgar博士の谜：错误信息&&exit
::if exist %play% (mplayer -loop 0 %play%) else (mplayer -loop 0 play.mp3)
::mplayer -vo caca 片头.rmvb
cls
title ⑥【剧场版：伦敦】  ◎制作：Cyxgg
color 3b
:set4
cls
start 开始.jpg
echo ╭──────────────────╮
echo │Edgar博士の谜剧场版：伦敦·选择界面 │
echo │                                    │
echo │    请根据图片选择：（1、2、3）     │
echo ╰──────────────────╯
choice /c 1234 >nul
goto s%errorlevel%
:s2
start 关于.jpg
cls
pause
goto set4
:s3
cls
start 设置.jpg
echo ╭──────────────────╮
echo │Edgar博士の谜剧场版：伦敦·游戏设置 │
echo │                                    │
echo │   请根据图片选择：（1、2、3、4）   │
echo ╰──────────────────╯
choice /c 1234 /n
goto set%errorlevel%
:s4
cls
call :input 输入存档密匙。 Edgar博士の谜存档
set ipbox=%ipbox:^i=%
set ipbox=%ipbox:^I=%
if not "%ipbox:~6,1%"=="" (call :msg 无法识别密匙。 16 Edgar博士の谜存档&goto set4)
if "%ipbox:~5,1%"=="" (call :msg 无法识别密匙。 16 Edgar博士の谜存档&goto set4)
if "%ipbox:~0,5%"=="A12NH" (set 烤地瓜=%ipbox:~5,1%&goto jczd)
call :msg 无法识别密匙。 16 Edgar博士の谜存档
goto set4
:set1
cls
echo ╭──────────────────╮
echo │Edgar博士の谜剧场版：伦敦·背景音乐 │
echo │请拖入音乐文件（最好mp3，no无音乐） │
echo │        或输入S再按Enter返回。      │
echo ╰──────────────────╯
set /p input=
if "%input%"=="" goto set1
if /i %input%==s goto s3
if /i %input%==no goto musicok
if not exist %input% call :msg 此文件不存在！ 16 Edgar博士の谜：错误信息&&goto s3
for %%i in (MP3,WMA,WAV,MOD,.RA,.CD,.MD,ASF) do if "%input:~-3%"=="%%i" goto musicok
echo WSH.Echo MsgBox("你选取的文件可能不是有效的音乐文件。是否继续？" 36 "Edgar博士の谜：确认信息")>%temp%\dep\msg.vbs
for /f %%i in ('cscript %temp%\dep\msg.vbs //nologo') do if %%i==2 (call :msg 已取消修改背景音乐的操作。 64 Edgar博士の谜：提示信息&&goto s3)
:musicok
echo.%input%>%temp%\dep\play.ini
call :msg 背景音乐设置成功，下起启动游戏时生效！,64,Edgar博士の谜：提示信息&&goto s3
:set2
cls
echo ╭──────────────────╮
echo │Edgar博士の谜剧场版：伦敦·背景图片 │
echo │  请替换本目录下同名图片文件即可。  │
echo │            按任意键返回。          │
echo ╰──────────────────╯
pause>nul
goto s3
:set3
cls
echo ╭──────────────────╮
echo │  Edgar博士の谜剧场版：伦敦·速度   │
echo │                                    │
echo │    1快速，2中速，3慢速，S返回。    │
echo ╰──────────────────╯
choice /c 123s /n
if %errorlevel%==4 goto s3
echo.%errorlevel%>%temp%\dep\ctime.ini
call :msg 速度设置成功，下起启动游戏时生效！,64,Edgar博士の谜：提示信息
goto s3
:s1
cls
mode con:cols=86 lines=27
echo                【Edgar博士の谜 剧场版：伦敦】【引子】【按K键快速继续】
choice /c k /t:%ctime% /d k >nul
echo.
choice /c k /t:%ctime% /d k >nul
echo     事件结束了！
choice /c k /t:%ctime% /d k >nul
echo     Felyme想：只要找到Oiiap就全部ok了，我也该休息一下了。。。
choice /c k /t:%ctime% /d k >nul
echo     正巧，这时候，弘假连锁的老板也到了FZB局：
choice /c k /t:%ctime% /d k >nul
echo     “我是弘假，你们局长在吗？我们是朋友。”
choice /c k /t:%ctime% /d k >nul
echo     FZB局助手：“哦，弘假先生吗？我去通知他一下。”
choice /c k /t:%ctime% /d k >nul
echo.
choice /c k /t:%ctime% /d k >nul
echo     不一会儿，Felyme来到会客室：
choice /c k /t:%ctime% /d k >nul
echo     “弘假，你有神马事情？”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“知道吗？弘假大厦已经竣工了！”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“嗯，我看了在线新闻。”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“所以，我想举办一个竣工的庆祝典礼。”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“……那么和我有神马关系？”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“我想和FZB局合作举办，为典礼添彩！”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“呃，行吧，我也正好破了真假Edgar案，一起庆祝好不好？”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“那真是太好了！对了，你也邀请Cyxgg、Edgar一起来吧！”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“好！”
choice /c k /t:%ctime% /d k >nul
echo.choice /c k /t:%ctime% /d k >nul
echo     突然，灯熄了！
color 0f
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“怎么，停电了？”
choice /c k /t:%ctime% /d k >nul
echo     “啊！”弘假在黑暗中叫道，“谁碰我？”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“助手，去启动太阳能电池！”
choice /c k /t:%ctime% /d k >nul
echo     “嗞嗞~~嗞嗞~~”灯亮了。
color 3b
choice /c k /t:%ctime% /d k >nul
echo     FZB局助手冲进会客室：“谁在这儿？”
choice /c k /t:%ctime% /d k >nul
echo     Felyme莫名其妙：“神马‘谁在这儿’？”
choice /c k /t:%ctime% /d k >nul
echo     FZB局助手挠了挠脑袋：“奇怪，我好像看到有人进来了。”
choice /c k /t:%ctime% /d k >nul
echo     弘假紧张地问：“刚才怎么会停电？”
choice /c k /t:%ctime% /d k >nul
echo     FZB局助手：“是保险丝断了……不过，好像有指纹，是人为的痕迹。”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“不管了，我们还是为庆典做准备吧！”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“好吧。。。但是。。。但是。。。”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“怎么了？”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“……还是算了吧。”
choice /c k /t:%ctime% /d k >nul
echo.
choice /c k /t:%ctime% /d k >nul
echo     再说Edgar的倒霉的发布会……
choice /c k /t:%ctime% /d k >nul
echo     观众甲：“零件差点飞到我头上了，可恶的Edgar！！！”
choice /c k /t:%ctime% /d k >nul
echo     Edgar：“失误。。。失误。。。”
choice /c k /t:%ctime% /d k >nul
echo     观众乙：“你能不能Debug全一下再发布啊？！！”
choice /c k /t:%ctime% /d k >nul
echo     Edgar：“失误。。。失误。。。”
choice /c k /t:%ctime% /d k >nul
echo     观众丙：“你能不能说完失误啊？？”
choice /c k /t:%ctime% /d k >nul
echo     Edgar：“失误。。。失误。。。”
choice /c k /t:%ctime% /d k >nul
echo     观众哈哈大笑……
choice /c k /t:%ctime% /d k >nul
echo.
choice /c k /t:%ctime% /d k >nul
echo     【准备好了吗？让我们开始在 Edgar博士の谜 中的冒险之旅！】
pause>nul
cls
color 2e
echo              【Edgar博士の谜 剧场版：伦敦】【竣工庆典】【按K键快速继续】
choice /c k /t:%ctime% /d k >nul
echo     弘假咖啡馆里……
choice /c k /t:%ctime% /d k >nul
start 弘假咖啡馆.jpg
echo    （按任意键继续）
pause>nul
echo     员工MIC：“弘假老板……那个……您最好别举办庆典了……”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“怎么可能？我要说到做到！”
choice /c k /t:%ctime% /d k >nul
echo     MIC：“但是……但是……”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“你别担心了，OK？”
choice /c k /t:%ctime% /d k >nul
echo     MIC：“哦……好吧……”
choice /c k /t:%ctime% /d k >nul
echo     弘假走向后台。
choice /c k /t:%ctime% /d k >nul
echo     MIC愣了一小会儿，然后继续布置起来。
choice /c k /t:%ctime% /d k >nul
echo.
choice /c k /t:%ctime% /d k >nul
echo     弘假在后台叹了一口气，摸出一张匿名信。
choice /c k /t:%ctime% /d k >nul
echo     弘假自我安慰：“这个东西，肯定是假的吧……”
choice /c k /t:%ctime% /d k >nul
echo     他把匿名信扔进了垃圾桶。
choice /c k /t:%ctime% /d k >nul
echo     这时，Felyme刚好到这里想与弘假商量一下，
choice /c k /t:%ctime% /d k >nul
echo     恰巧看到了垃圾桶里的匿名信。
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“What's this？”
choice /c k /t:%ctime% /d k >nul
echo     于是，Felyme捡了起来。
choice /c k /t:%ctime% /d k >nul
start 匿名信.jpg
echo     （按任意键继续）
pause>nul
echo     Felyme：“这？”
choice /c k /t:%ctime% /d k >nul
echo     Felyme快步赶到弘假办公室：“这是怎么回事？”
choice /c k /t:%ctime% /d k >nul
echo     弘假轻描淡写：“哦，一个朋友的恶作剧。”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“……哦……”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“你来得正好，我们商量一下竣工庆典吧。”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“……好吧……”
choice /c k /t:%ctime% /d k >nul
echo.
choice /c k /t:%ctime% /d k >nul
echo     Felyme和弘假讨论到一半，
choice /c k /t:%ctime% /d k >nul
echo     忽然一个人推门而入：“Sorry，打扰了，但这真的是一件重要的事。”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“你是？”
choice /c k /t:%ctime% /d k >nul
echo     来人说：“我是BSBNZ！”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“你是奶茶烧饼店的继承人？？？”
choice /c k /t:%ctime% /d k >nul
echo     BSBNZ：“是啊，但我和Oiiap没关系，奶茶烧饼店已经不归他管了！”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“嗯。。。Oiiap现在被全球通缉呢。。。”
choice /c k /t:%ctime% /d k >nul
echo     BSBNZ脸绿了。
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“怎么了？”
choice /c k /t:%ctime% /d k >nul
echo     BSBNZ：“额……没啥……我今天来，就是想和弘假先生聊下。”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“神马事？”
choice /c k /t:%ctime% /d k >nul
echo     BSBNZ：“听说您的大厦竣工了，要举办庆典？”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“是的……”
choice /c k /t:%ctime% /d k >nul
echo     BSBNZ：“所以，我想赞助一下~~~~~~”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“哦……好吧！奶茶烧饼店是吧？”
choice /c k /t:%ctime% /d k >nul
echo     BSBNZ：“是的。我还想一起去London。”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“……你来参加旅游团的？”
choice /c k /t:%ctime% /d k >nul
echo     BSBNZ：“不不不……这只是顺便，顺便！”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“赞助费呢？”
choice /c k /t:%ctime% /d k >nul
echo     BSBNZ：“5杯奶茶……哦不，你要可以再添。”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“……（这家伙是来砸场子的吗）”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“OKAY！”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“喂喂……（我还没表态呢）”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“你可要给我们提供Oiiap的信息！”
choice /c k /t:%ctime% /d k >nul
echo     BSBNZ：（再次脸绿）“好！”
choice /c k /t:%ctime% /d k >nul
echo     送走BSBNZ，弘假说：“Felyme，我们需要准备一些东西……”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“好说！要神马？”
choice /c k /t:%ctime% /d k >nul
echo     弘假说：“嗯。。。我有一个表单。”
choice /c k /t:%ctime% /d k >nul
echo     ┏━━━━━━━━┓
choice /c k /t:%ctime% /d k >nul
echo     ┃                ┃
choice /c k /t:%ctime% /d k >nul
echo     ┃    %ju%元酒    ┃
choice /c k /t:%ctime% /d k >nul
echo     ┃                ┃
choice /c k /t:%ctime% /d k >nul
echo     ┃   %dg%元蛋糕   ┃
choice /c k /t:%ctime% /d k >nul
echo     ┃                ┃
choice /c k /t:%ctime% /d k >nul
echo     ┃   %s%个保安    ┃
choice /c k /t:%ctime% /d k >nul
echo     ┃                ┃
choice /c k /t:%ctime% /d k >nul
echo     ┗━━━━━━━━┛
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“What？这不是你该找的吗？”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“这是最轻松的活了。。。不然人家会说FZB局是打酱油的。”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“额……”
choice /c k /t:%ctime% /d k >nul
echo     弘假：“而且FZB局人多，可以当保安，竣工庆典的时间也你定。”
choice /c k /t:%ctime% /d k >nul
echo     Felyme（勉强地）：“好吧。。。”
choice /c k /t:%ctime% /d k >nul
echo.
choice /c k /t:%ctime% /d k >nul
echo     Felyme从弘假咖啡馆出来，想：“现在该到哪里去呢？”
choice /c k /t:%ctime% /d k >nul
mode con:cols=33 lines=13
set tishi=数字键选择，K操作，J物品
:buy
if %dg%%ju%==00 goto qingdian
cls
echo ┏━━━━┳━━━━┳━━━━┓
echo ┃   ①   ┃   ②   ┃   ③   ┃
echo ┃五猩酒店┃远祖蛋糕┃笨驰汽车┃
echo ┡━━━━┻━━━━┻━━━━┩
echo ┆ 坑    爹    一    条    街 ┆
echo ┢━━━━┳━━━━┳━━━━┪
echo ┃小 揪 坊┃舔 品 店┃ 输  店 ┃
echo ┃   ④   ┃   ⑤   ┃   ⑥   ┃
echo ┗━━━━┻━━━━┻━━━━┛
echo  →%tishi%
choice /c 123456jk >nul
set panduan=%errorlevel%
if %panduan%==7 goto wupin
if %panduan%==8 set tishi=目前没有可用的操作！         &goto buy
set tishi=又回来了。。。               
goto buy%panduan%
:buy1
cls
echo 【五猩酒店】
choice /c k /t:%ctime% /d k >nul
start 五猩酒店.png
echo     （按任意键继续）
pause>nul
choice /c k /t:%ctime% /d k >nul
echo Felyme：“我买酒！”
choice /c k /t:%ctime% /d k >nul
echo 服务员：“哦，要多少？”
choice /c k /t:%ctime% /d k >nul
echo Felyme：“%ju%元的！”
choice /c k /t:%ctime% /d k >nul
echo 服务员：“对面才是酒坊。”
choice /c k /t:%ctime% /d k >nul
echo 服务员：“这里是宾馆，要住吗？”
choice /c k /t:%ctime% /d k >nul
echo Felyme：“我没住宾馆，抱歉……”
choice /c k /t:%ctime% /d k >nul
echo Felyme退了出去。
choice /c k /t:%ctime% /d k >nul
goto buy
:buy2
cls
echo 【远祖蛋糕】
choice /c k /t:%ctime% /d k >nul
echo Felyme：“我买蛋糕！”
choice /c k /t:%ctime% /d k >nul
echo 售货员：“哦，要多少？”
choice /c k /t:%ctime% /d k >nul
echo Felyme：“%dg%元的！”
choice /c k /t:%ctime% /d k >nul
echo 售货员：“没有，最便宜99999元！”
choice /c k /t:%ctime% /d k >nul
echo Felyme：“别说你们买蛋糕送钻石啊！”
choice /c k /t:%ctime% /d k >nul
echo Felyme晕死，赶紧退出去。
choice /c k /t:%ctime% /d k >nul
goto buy
:buy3
cls
echo 【笨驰汽车】
choice /c k /t:%ctime% /d k >nul
echo         ┏━━━━━┓
echo ┏━━━┫ 笨驰汽车 ┣━━━┓
echo ┃      ┗━━━━━┛      ┃
echo ┃  现在做神马呢？          ┃
echo ┃                   ____   ┃
echo ┃  S 返回          /    \  ┃
echo ┃  K 购买        ╱￣￣￣╲┃
echo ┃                 ▌￣￣ ▌┃
echo ┃┄┄┄┄┄┄┄┄┄┄┄┄┄┃
choice /c sk >nul
if %errorlevel%==1 goto buy
call :input 请输入要购买的车型。 笨驰汽车
if %ipbox%1==1 goto buy3
call :msg 购买成功！ 64 笨驰汽车
if %ipbox%==KDG-%dg1% (if not %dg1%==0 set /a 烤地瓜+=1&set dg1=0&echo 车里有一个地瓜！&ping/n 3 127.1>nul)
goto buy3
:buy4
cls
echo 【小揪坊】
set /a jiu1=%random%%%10+10
set /a jiu2=%random%%%10+10
set /a jiu3=%random%%%10+10
choice /c k /t:%ctime% /d k >nul
echo 老板：“这么多种酒，要哪种？”
choice /c k /t:%ctime% /d k >nul
echo Felyme：“我选选。。。”
echo ①%jiu1%元/L
echo ②%jiu2%元/L
echo ③%jiu3%元/L
echo S返回
choice /c 123ns /t 7 /d n >nul
set err=%errorlevel%
if %err%==4 goto buy4
if %err%==5 goto buy
set /a jiu4=%ju%%%!jiu%err%!
if %jiu4%==0 (echo 正好！Felyme高兴地走了。&ping/n 3 127.1>nul&set /a dg1=%random%%%99+1&set ju=0&goto buy)
echo 真不巧，不能凑齐%ju%元的酒……
set dg1=0
choice /c k /t:%ctime% /d k >nul
goto buy4
:buy5
cls
echo 【舔品店】
choice /c k /t:%ctime% /d k >nul
set /a dgg1=%random%%%10+10
set /a dgg2=%random%%%10+10
set /a dgg3=%random%%%10+10
choice /c k /t:%ctime% /d k >nul
echo 老板：“这么多蛋糕，要哪种？”
choice /c k /t:%ctime% /d k >nul
echo Felyme：“我选选。。。”
echo ①%dgg1%元/L
echo ②%dgg2%元/L
echo ③%dgg3%元/L
echo S返回
choice /c 123ns /t 7 /d n >nul
set err=%errorlevel%
if %err%==4 set dg1=0&goto buy5
if %err%==5 goto buy
set /a jiu4=%dg%%%!dgg%err%!
if %jiu4%==0 (echo 正好！Felyme高兴地走了。&set /a dg1=%random%%%99+1&ping/n 3 127.1>nul&set dg=0&goto buy)
echo 真不巧，不能凑齐%ju%元的蛋糕……
set dg1=0
choice /c k /t:%ctime% /d k >nul
goto buy5
:buy6
cls
echo ╔━━━━━━━━━━━━━━╗
echo ┃        DEC连锁-输店        ┃
echo ╠┄┄┄┄┄┄┄┄┄┄┄┄┄┄╣
echo ┃    地瓜一下，你不知道！    ┃
echo ┃     中国图书最烂的书店     ┃
echo ┃    不是洋品牌，而是地瓜    ┃
echo ╚━━━━━━━━━━━━━━╝
echo 输入要买的书：（S返回）
set /p input=
if %input%1==1 goto buy6
if /i %input%==s goto buy
if %input%==地瓜手册 echo.地瓜号：%dg1%
call :msg 购买成功！ 64 输店
goto buy6
:qingdian
cls
mode con:cols=86 lines=27
color 0c
echo     Felyme在FZB局找了几个助手当保安，高高兴兴地去参加庆典。
choice /c k /t:%ctime% /d k >nul
echo     但是，BSBNZ在暗地里冷笑着：“什么FZB局，什么弘假连锁，今天就在我的巨型烟花里灭绝吧！哈哈哈哈哈哈哈……”
choice /c k /t:%ctime% /d k >nul
echo.
choice /c k /t:%ctime% /d k >nul
echo     弘假庆典……
choice /c k /t:%ctime% /d k >nul
start 弘假庆典.jpg
echo     （按任意键继续）
pause>nul
echo     弘假正在致词：“大家好，我是弘假老板！在这个值得庆贺的日子里，弘假大厦终于竣工了……”
choice /c k /t:%ctime% /d k >nul
echo     Felyme在下面工作，忽然他的FZB局旗舰手机响了。
choice /c k /t:%ctime% /d k >nul
echo     Felyme走到一边，低声说：“喂？谁？”
choice /c k /t:%ctime% /d k >nul
echo     对方：“我是Cyxgg，有……”
choice /c k /t:%ctime% /d k >nul
echo     Felyme说：“哦，Cyxgg啊，你也参加了庆典的呀，直接找我就行了啊，干嘛打电话？”
choice /c k /t:%ctime% /d k >nul
echo     Cyxgg焦急地说：“说来话长……没时间说这个了，赶紧……”
choice /c k /t:%ctime% /d k >nul
echo.
choice /c k /t:%ctime% /d k >nul
echo     弘假正在台上说：“根据WINCIOS Pro随机抽选，今天得到伦敦游的幸运嘉宾是——”
choice /c k /t:%ctime% /d k >nul
echo     Edgar想：“快说，041号Edgar，041号Edgar！”
choice /c k /t:%ctime% /d k >nul
echo     “049号Cyxgg！大家鼓掌！”
choice /c k /t:%ctime% /d k >nul
echo     Edgar郁闷：“早知道我在WINCIOS里面加个彩蛋……”
choice /c k /t:%ctime% /d k >nul
echo.
choice /c k /t:%ctime% /d k >nul
echo     Felyme高兴地说：“Cyxgg你被抽中了呀！伦敦游！祝贺！”
choice /c k /t:%ctime% /d k >nul
echo     Cyxgg说：“没时间了！还有10分钟！定时炸弹……”
choice /c k /t:%ctime% /d k >nul
echo     Felyme的笑容凝住了：“神马？”
choice /c k /t:%ctime% /d k >nul
set /a zdf=%random%%%19+1
echo     Cyxgg：“炸弹……快点……%zdf%F……if 密码……没引号……”
choice /c k /t:%ctime% /d k >nul
echo     信号断了，电话也断了，Felyme着急：“这破信号！”
choice /c k /t:%ctime% /d k >nul
echo     看着弘假还在激情昂扬地演讲，Felyme想：
choice /c k /t:%ctime% /d k >nul
echo     “如果说出这个消息，肯定会引起大乱，况且还不知道这是不是真的……”
choice /c k /t:%ctime% /d k >nul
echo     “那么，我先去找找……Cyxgg说的是应该在%zdf%楼吧……他后面说的又是神马呢？”
choice /c k /t:%ctime% /d k >nul
echo     想到这里，Felyme拿起FZB局旗舰手机，通过语音记录记下了Cyxgg的话。
choice /c k /t:%ctime% /d k >nul
echo     Felyme进入电梯：“嗯……该去几楼呢？15分钟……只有900秒了。”
choice /c k /t:%ctime% /d k >nul
color 8f
set tishi1=单击要去的楼层。
set tishi2=获取帮助请点提示栏！
set zdtime=600
:dianti
mode con:cols=27 lines=32
set go=dianti
cls
echo ┏━━━━━━━━━━━┓
echo ┃Ｗ┏━┓┏━┓┏━┓０┃
echo ┃Ｉ┃18┃┃19┃┃20┃Ｆ┃
echo ┃Ｎ┗━┛┗━┛┗━┛闲┃
echo ┃Ｃ┏━┓┏━┓┏━┓人┃
echo ┃Ｉ┃15┃┃16┃┃17┃勿┃
echo ┃Ｏ┗━┛┗━┛┗━┛入┃
echo ┃Ｓ┏━┓┏━┓┏━┓  ┃
echo ┃　┃12┃┃13┃┃14┃防┃
echo ┃弘┗━┛┗━┛┗━┛火┃
echo ┃假┏━┓┏━┓┏━┓、┃
echo ┃连┃９┃┃10┃┃11┃防┃
echo ┃锁┗━┛┗━┛┗━┛爆┃
echo ┃电┏━┓┏━┓┏━┓由┃
echo ┃梯┃６┃┃７┃┃８┃Ｆ┃
echo ┃控┗━┛┗━┛┗━┛Ｚ┃
echo ┃制┏━┓┏━┓┏━┓Ｂ┃
echo ┃智┃３┃┃４┃┃５┃局┃
echo ┃能┗━┛┗━┛┗━┛提┃
echo ┃版┏━┓┏━┓┏━┓供┃
echo ┃  ┃０┃┃１┃┃２┃支┃
echo ┃  ┗━┛┗━┛┗━┛持┃
echo ┗━━━━━━━━━━━┛
echo ╔━━━━提示栏━━━━╗
echo ┃                      ┃
echo ┃                      ┃
echo ╚━━━━━━━━━━━╝
cmos 0 0 1 2 24
echo %tishi1%
cmos 0 0 1 2 25
echo %tishi2%
ping/n 2 127.1>nul
cmos 0 -1 1
set /a dj=%errorlevel%
set /a dja=%dj:~0,-3%
set /a djb=%dj%-1000*%dja%
if %dja% lss 3 goto dianti
if %dja% gtr 24 goto dianti
if %djb% gtr 23 if %djb% lss 25 (goto dianti) else (if %djb% lss 27 goto gamehelp)
set /a gol=24-%djb%
set /a gol2=%gol%%%3
if not %gol2%==0 goto dianti
set /a gol=%gol%/3
set /a gol2=(%dja%+1)/2
set /a gol3=(%gol2%-1)%%3
if not %gol3%==0 goto dianti
set /a gol2=(%gol2%-1)/3
set /a gol=%gol%*3+%gol2%-4
set /a zdtime-=30
wj
call :msg 电梯到了%gol%楼。 64 弘假大厦电梯
if %gol%==%zdf% goto zdl
set tishi2=到了%gol%楼，不对啊！&set tishi1=用去30秒，还有%zdtime%秒。
if %gol%==0 goto hjdsw
goto dianti
:zdl
set round=1
set wz1=5
set wz2=9
set a1=北
set a2=西
set a3=南
set a4=东
set b1=1-1
set b2=2-2
set b3=1+1
set b4=2+2
mode con:cols=22 lines=17
cls
echo   1 2 3 4 5 6 7 8 9 x
echo 1┏┳┳┳┳┳┳┳┓%zdf%
echo 2┣╋╋╋╋╋╋╋┫楼
echo 3┣╋╋╋╋╋╋╋┫：
echo 4┣╋╋╋╋╋╋╋┫大
echo 5┣╋╋╋◎╋╋╋┫厅
echo 6┣╋╋╋╋╋╋╋┫平
echo 7┣╋╋╋╋╋╋╋┫面
echo 8┣╋╋╋╋╋╋╋┫图
echo 9┗┻┻┻┻┻┻┻┛↑
echo y 你的位置：(5,5)  北
echo 有声音，在--方！
echo READY？按任意键继续。
echo 还有%zdtime%秒，加油！
pause>nul
cmos 0 0 1 0 12
echo 注意：WASD移动       
:zdl2
set /a a=%random%%%4+1
set b=!b%a%!
set /a c=!wz%b:~0,1%!%b:~1,2%
if %c% lss 1 goto zdl2
if %b%==1 if %c% gtr 9 goto zdl2
if %b%==2 if %c% gtr 17 goto zdl2
cmos 0 0 1 10 11
echo.!a%a%!
cmos 0 0 1 4 13
echo.%zdtime%
choice /c wasdn /t 3 /d n >nul
set err=%errorlevel%
if %err%==5 call :msg GAME OVER！你找不到声音了。 48 GAME OVER！&&exit
if not %err%==%a% call :msg GAME OVER！你找不到声音了。 48 GAME OVER！&&exit
cmos 0 0 1 %wz2% %wz1%
if %wz1%%wz2%==11 echo ┏&goto zdnext
if %wz1%%wz2%==117 echo ┓&goto zdnext
if %wz1%%wz2%==91 echo ┗&goto zdnext
if %wz1%%wz2%==917 echo ┛&goto zdnext
if %wz1%==1 echo ┳&goto zdnext
if %wz1%==9 echo ┻&goto zdnext
if %wz2%==1 echo ┣&goto zdnext
if %wz2%==17 echo ┫&goto zdnext
echo ╋
:zdnext
set /a wz!b%a%:~0,1!=%c%
cmos 0 0 1 %wz2% %wz1%
echo ◎
set /a round+=1
set /a zdtime-=20
if not %round%==11 goto zdl2
cls
echo Felyme找到了炸弹！
choice /c k /t:%ctime% /d k >nul
echo 但是，炸弹很难破解啊……
choice /c k /t:%ctime% /d k >nul
echo 忽然，Felyme看到一行字：MS-DOS批处理程序
choice /c k /t:%ctime% /d k >nul
echo Felyme：天助我也！我是BAT高手啊。
choice /c k /t:%ctime% /d k >nul
echo 但是，怎么破解呢？
choice /c k /t:%ctime% /d k >nul
echo Felyme翻出了FZB局BAT破解手册……
choice /c k /t:%ctime% /d k >nul
cls
echo ┏━━━━━━━━┓
echo ┃Cyxgg的话：     ┃
echo ┃if 密码…没引号 ┃
echo ┃可用破解语言：  ┃
echo ┃①1==1 if 1     ┃
echo ┃②1==2 if 1     ┃
echo ┃③1==1 if not 1 ┃
echo ┃④1==2 if not 1 ┃
echo ┃1、2、3、4选择  ┃
echo ┗━┳━━━━┳━┛
echo     ┃剩余   s┃
echo     ┗━━━━┛
:cczd
cmos 0 0 1 10 10
if %ztime% lss 100 (echo.%zdtime% ) else (echo.%zdtime%)
choice /c 1234n /t 1 /d n >nul
set /a zdtime-=15
if %zdtime% lss 1 call :gameover 时间不够了，炸弹爆炸了！你失败了。。。
if %errorlevel%==5 goto cczd
if not %errorlevel%==3 call :gameover 拆除失败，炸弹爆炸了！你失败了。。。
call :msg 当跨越3的所在，便能保存真相：A12NH%烤地瓜% 32 Edgar博士の谜：讯息
:jczd
cls
color 0c
mode con:cols=86 lines=27
echo.
choice /c k /t:%ctime% /d k >nul
echo     Felyme成功解除了炸弹！Felyme想：“真的有人盯上弘假了……但Cyxgg在哪儿呢？”
choice /c k /t:%ctime% /d k >nul
echo     这时，旁边一个房间传出声音：“唔喂额嗯咿……”
choice /c k /t:%ctime% /d k >nul
echo     Felyme想进门，但门锁着了。
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“里面是谁？我来撞开它！”
choice /c k /t:%ctime% /d k >nul
echo     “1、2、3、撞……”“砰！”门开了。
choice /c k /t:%ctime% /d k >nul
echo     只见Cyxgg在里面，嘴被堵住了，手也被捆住了。
choice /c k /t:%ctime% /d k >nul
echo     Felyme急忙帮他解开，问：“怎么回事？”
choice /c k /t:%ctime% /d k >nul
echo     Cyxgg说：“是……啊，你身后！”
choice /c k /t:%ctime% /d k >nul
echo     Felyme一回头，一个蒙面人拿刀对着自己！
choice /c k /t:%ctime% /d k >nul
echo     这时，FZB局Felyme的警卫顺着FZB-GPS到了这里，赶紧迎上去。
cls
mode con:cols=33 lines=17
echo ╔游戏开始！═════════╗
echo ║          游戏规则介绍      ║
echo ║                            ║
echo ║    这是一个搏斗游戏！      ║
echo ║规则很简单，蒙面人出右（→）║
echo ║你就应该往左边（←）躲，出上║
echo ║（↑）你就该往下面（↓）躲。║
echo ║如果生命为0你就输了，如果50 ║
echo ║轮你还有HP，蒙面人AP能量没有║
echo ║了，你便赢了！              ║
echo ║    准备好了吗？            ║
echo ║                            ║
echo ║                 按E键继续。║
echo ╚══════════════╝
choice /c e >nul
mode con:cols=31 lines=6
for /l %%i in (5,-1,1) do (
cls
echo ┏━━━━━━━━━━━━━┓
echo ┃还有%%i秒开始，请准备！     ┃
echo ┗━━━━━━━━━━━━━┛
choice /c q /t 1 /d q >nul
)
set f=1
set 3=↑
set 4=←
set 1=↓
set 2=→
:qte
set /a r=1+%random%%%4
set a%f%=!%r%!
set /a f+=1
if not %f%==51 goto qte
set a51=-
set hp=150
set ap=100
set b1=↑
set b2=←
set b3=↓
set b4=→
set b5=－
set qd=－
set ctime=2
set round=1
set hps=5
set hpsj=1
for /l %%i in (1,1,5) do set t%%i=                          
mode con:lines=17
:qtegame
cls
echo     ┏━━━━┳━━━━┓
echo     ┃警卫    ┃蒙面人  ┃
echo     ┣┉┉┉┉╋┉┉┉┉┫
echo     ┃HP：%hp% ┃AP：%ap% ┃
echo     ┃  ╭─╮┃  ╭─╮┃
echo     ┃躲│%qd% │┃出│!a%round%! │┃
echo     ┃闪╰─╯┃招╰─╯┃
echo ┏━┛┉┉┉┉┻┉┉┉┉┗━┓
echo ┃%t1%┃
echo ┃%t2%┃
echo ┃%t3%┃
echo ┃%t4%┃
echo ┃%t5%┃
echo ┗━━━━━━━━━━━━━┛
echo →第%round%回合！
choice /c wasdn /t:%ctime% /d n >nul
set qd=%errorlevel%
if %ap%==0 goto winqte
set /a ap-=2
if %ap% lss 100 set ap=%ap% 
if %ap% lss 10 set ap=%ap% 
if %round%==41 (
set t1=%t2%
set t2=%t3%
set t3=%t4%
set t4=%t5%
set t5=蒙面人急了！他加快了速度。
set ctime=1
)
if !%qd%!==!a%round%! goto qteok
set qd=!b%qd%!
set /a round+=1
set /a hp-=%hps%
if %hp% lss 1 call :gameover 你被蒙面人打倒了！
set t1=%t2%
set t2=%t3%
set t3=%t4%
set t4=%t5%
if %hps% lss 10 set hps=%hps% 
if %hpsj%==1 (set t5=警卫受到攻击！HP减少%hps%。  ) else (set t5=%hpsj%连击！警卫HP减少%hps%。  )
set /a hpsj+=1
set /a hps+=%hpsj%
if %hp% lss 100 set hp=%hp% 
if %hp% lss 10 set hp=%hp% 
goto qtegame
:qteok
set qd=!b%qd%!
set /a round+=1
set hpsj=1
set hps=5
goto qtegame
:winqte
echo.
choice /c k /t:%ctime% /d k >nul
echo     蒙面人没力气了，赶紧跑了。警卫退下去，Felyme追出去，没看见一个人影。
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“倒霉，让他逃了！对了，Cyxgg，你这是怎么回事？”
choice /c k /t:%ctime% /d k >nul
echo     Cyxgg说：“我正参加宴会，忽然觉得眼睛一黑，被人重重地打晕了……”
choice /c k /t:%ctime% /d k >nul
echo     Felyme晕：“你怎么每次都那么倒霉。”
choice /c k /t:%ctime% /d k >nul
echo     Cyxgg接着说：“然后，我醒了，眼前有一个蒙面人。他没发觉我……”
choice /c k /t:%ctime% /d k >nul
echo     “我听到他说：‘哈哈，炸弹安好了，该走了……’”
choice /c k /t:%ctime% /d k >nul
echo     “我大吃一惊：‘炸弹？’然后，蒙面人说：‘用批处理判定应该没问题吧。’”
choice /c k /t:%ctime% /d k >nul
echo     “他接着说：‘解除炸弹密码只有我知道，判定嘛……就用if 密码==XXXXXX goto来判定吧。’”
choice /c k /t:%ctime% /d k >nul
echo     “我模糊记得楼层，便等他走后，打电话给你……”
choice /c k /t:%ctime% /d k >nul
echo     “但是，电话信号突然断了，抬头一看，蒙面人拿着高赫兹信号干扰器在面前！”
choice /c k /t:%ctime% /d k >nul
echo     “然后，不知怎么回事，就是一顿打……便这样了。”
choice /c k /t:%ctime% /d k >nul
echo     Felyme：“我们赶紧回去找弘假吧。我去报警，顺便给FZB局保卫部通知一下。”
choice /c k /t:%ctime% /d k >nul
echo     于是，他们回到了1F。
choice /c k /t:%ctime% /d k >nul
echo     弘假听说此事，镇定地说：“嗯……既然解决了就不管了吧，我以后注意一点。”
choice /c k /t:%ctime% /d k >nul
echo     Cyxgg急忙说：“可是……”
choice /c k /t:%ctime% /d k >nul
echo     弘假摆手：“以后再处理吧。如果影响到庆典和伦敦游怎么办？”
choice /c k /t:%ctime% /d k >nul
echo     Cyxgg想到了伦敦游：“哦，那算了。”







:hjdsw
set zimu=QERTYUPADFGHJKLZXVBM
set num=1
mode con:lines=40
:hjdsw2
set /a a=%random%%%20
set mm%num%=!zimu:~%a%,1!
set /a num+=1
if not %num%==22 goto hjdsw2
set /a a1=%random%%%3+1
set mm%a1%=W
set /a a2=%random%%%3+4
set mm%a2%=I
set /a a3=%random%%%3+7
set mm%a3%=N
set /a a4=%random%%%3+10
set mm%a4%=C
set /a a5=%random%%%3+13
set mm%a5%=I
set /a a6=%random%%%3+16
set mm%a6%=O
set /a a7=%random%%%3+19
set mm%a7%=S
set num=7
mode con:lines=15
cls
echo ╔━━━━━━━━━━━╗
echo ┃   弘假大厦-食品仓库  ┃
echo ╠━━━━━━━━━━━╣
echo ┃密码系统：点击不符的字┃
echo ┃或短语来开启仓库。    ┃
echo ┃ %mm1%  %mm2%  %mm3%  %mm4%  %mm5%  %mm6%  %mm7%  ┃
echo ┃ %mm8%  %mm9%  %mm10%  %mm11%  %mm12%  %mm13%  %mm14%  ┃
echo ┃ %mm15%  %mm16%  %mm17%  %mm18%  %mm19%  %mm20%  %mm21%  ┃
echo ┃烤地瓜个数：%烤地瓜%         ┃
echo ╚━━━━↓回去━━━━╝
:sbck
ping/n 2 127.1>nul
cmos 0 -1 1
set /a dj=%errorlevel%
set /a dja=%dj:~0,-3%
set /a djb=%dj%-1000*%dja%
if %djb%==10 (if %dja% gtr 10 if %dja% lss 17 goto dianti)
set /a djb-=6
if %djb% lss 0 goto sbck
if %djb% gtr 2 goto sbck
set /a a=(%dja%-1)%%3
if not %a%==0 goto sbck
set /a dja=(%dja%-1)/3
if %dja%==8 goto sbck
echo. 
set /a mmnum=%djb%*7+%dja%
for /l %%i in (1,1,%num%) do (if %mmnum%==!a%%i! set dg2=0)
if %num%==20 if 1%dg2%==10 (goto sbck) else (call :msg 仓库打开，有一个烤地瓜！ 64 烤地瓜&set /a 烤地瓜+=1)
set /a num+=1
set a%num%=%mmnum%
goto sbck





















:gamehelp
set help=2
cmos 0 0 1 4 %help%
echo ╔━━游戏帮助━━╗
set /a help+=1
cmos 0 0 1 4 %help%
echo ┃WASD移动   K操作┃
set /a help+=1
cmos 0 0 1 4 %help%
echo ┃J物品   部分鼠标┃
set /a help+=1
cmos 0 0 1 4 %help%
echo ┃请具体根据提示栏┃
set /a help+=1
cmos 0 0 1 4 %help%
echo ┃   进行操作！   ┃
set /a help+=1
cmos 0 0 1 4 %help%
echo ┃ Cyxgg CopyRight┃
set /a help+=1
cmos 0 0 1 4 %help%
echo ┃  (C)2010-2013  ┃
set /a help+=1
cmos 0 0 1 4 %help%
echo ┗━━━━━━━━×
cmos 0 -1 1
set /a dj=%errorlevel%
set /a dja=%dj:~0,-3%
set /a djb=%dj%-1000*%dja%
if %djb%==10 if dja gtr 22 (if %dja% lss 25 goto %go%)
goto gamehelp
:gameover
cls
mode con:cols=29 lines=15
mplayer -vo caca 失败.rmvb
cls
title 你失败了！
wj
for %%i in (0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f) do (color 4%%i&ping/n 1 127.1>nul)
echo.%1
echo SORRY，请按任意键退出...
pause>nul
exit
:msg
echo msgbox "%1",%2,"%3">1.vbs
start /wait 1.vbs
del 1.vbs
goto :eof
:input
echo WSH.Echo InputBox ("%1","%2")>1.vbs
for /f "delims= " %%i in ('cscript 1.vbs //nologo') do (set "ipbox=%%i")
del 1.vbs
goto :eof