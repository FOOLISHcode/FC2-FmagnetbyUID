# FC2-FmagnetbyUID Ver 1.0


用于根据FC2官网作品对应的作者作品页网址搜索该作者所有作品号并尝试获取作品磁链，最终形成网页列表的傻瓜式小工具，方便仓鼠用户批量下载
#

☆★该工具理论上与[FC2-FREE-list](https://github.com/FOOLISHcode/FC2-FREE-list "FC2-FREE-list")可以共存于同一文件夹★☆<br>
可公用config.ini、home.html文件<br>
可公用/data、/pic、/js文件夹

#
使用方法（仅适合windows 10环境，win7需要自行安装环境包）：

1.下载FC2-FmagnetbyUID.zip.001和FC2-FmagnetbyUID.zip.002并解压缩到任意位置

2.在config.ini选择是否代理及是否下载预览原图（选填，不更改将使用默认配置运行）

3.双击FmagnetbyUID.exe→输入4，回车→输入作者页链接（如`https://xxxx.contents.xx2.com/users/xxxxxx/articles?sort=date&order=desc`），回车→等待爬虫程序爬完列表资源（速度快慢由你的网络环境决定）

4.（可选步骤）输入3，回车→输入作者UID（可在/data文件夹生成的xxxxxx.xlsx文件找到，xxxxxx即为作者UID），回车→等待爬虫程序爬完图片资源（速度快慢由你的网络环境决定）

5.打开home.html→选择文件（./data/FC2_ALL.xlsx）→enjoy或者直接打开/data文件夹xxxxxx.xlsx文件直接查看



#

推荐的文件存放树：

./

├FmagnetbyUID.exe

├config.ini

├home.html

├data/

┊    └───...

├pic/

┊    ├───nodata.jpg

┊    ├───new.jpg

┊    └───...

└js/

┊    └───xlsx.mini.js
     
以上！

不对代码安全性，程序可用性做出保证，如有需要，请自行检查并修改代码，或自建环境自行编译：

pyinstaller -F FmagnetbyUID.py -p Config.py --hidden-import Config.py 
