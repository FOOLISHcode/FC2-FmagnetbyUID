import pandas as pd
import parsel
import requests
import warnings
import time
import os
import Config
import threading

author_name = ''

class Download_Thread (threading.Thread):
    def __init__(self, threadID, this_url_num, isproxy, pic_url, http_proxy, https_proxy, i):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.this_url_num = this_url_num
        self.isproxy = isproxy
        self.pic_url = pic_url
        self.http_proxy = http_proxy
        self.https_proxy = https_proxy
        self.i = i
    def run(self):
        #print ("开始线程：" + self.threadID)
        downloadpic(self.this_url_num, self.isproxy,self.pic_url,self.http_proxy,self.https_proxy,self.i)
        #print ("退出线程：" + self.threadID)

def getresponse (isproxy,url,http_proxy,https_proxy):
    proxies = {'http': http_proxy, 'https': https_proxy}
    #定义代理地址
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}
    #定义访问头
    i = 0
    while i < 3:
        try:
            if isproxy == 'yes':                   
                response = requests.get(url=url,headers=headers,proxies=proxies,verify=False,timeout=5)
                #get(链接地址，访问头，代理端口，不检测ssl证书)
                return response
            elif isproxy == 'no':
                    #print('不使用代理')
                    response = requests.get(url=url,headers=headers,verify=False,timeout=5)
                    #get(链接地址，访问头，不检测ssl证书)
                    return response               
        except Exception as e:
            #print(e)
            i += 1
            time.sleep(5)

#单机版简化链接
# def getresponse(link):
#     header = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}
#     http_proxy = 'http://127.0.0.1:7890'
#     https_proxy = 'http://127.0.0.1:7890'
#     proxies = {'http': http_proxy, 'https': https_proxy}
#     i=0
#     while i<3:
#         try:
#             response = requests.get(url=link,proxies=proxies,headers=header,verify=False,timeout=5)
#             return response
#         except Exception as e:
#             #print(e)
#             i=i+1
#             time.sleep(2)
#     return 0

def downloadpic(this_url_num,isproxy,pic_url,http_proxy,https_proxy,i):
    
    #print(pic_url)
    pic_response = getresponse(isproxy,pic_url,http_proxy,https_proxy)
    if pic_response !='0':
        pic_data = pic_response.content
        pic_filename = './pic/%s_%s.jpg' % (this_url_num,i+1)
        with open(pic_filename,'wb') as f:
            f.write(pic_data)
            print('%s_%s.jpg 下载完毕' % (this_url_num,i+1))
            f.close
    else:
        print('%s_%s.jpg 下载失败' % (this_url_num,i+1))

def getpic():            
    
    try:
        author = input('输入作者名：')
        filename = f'./data/{author}.xlsx'
        print(filename)
        all_df = pd.read_excel(filename)
    except Exception as e:
        input('没有该作者信息')
        return 
    num_list = all_df['num']

    #获取config.ini配置参数
    getconfig = Config.Config()
    isproxy = getconfig.isproxy
    http_proxy = getconfig.http_proxy
    https_proxy = getconfig.https_proxy
    isdown_bigpic = getconfig.isdown_bigpic
    getconfig.printconfig()

    #2.获取正确的链接地址列表（将得到num值与fc2官网寻找页面结合形成列表
    links_list = []
    for num in num_list:
        links_list.append('https://adult.contents.fc2.com/article/%s/' % num)
    #3.发送网络请求（获得完整html代码）
    tiktok = 0
    sum = 0

    for url in links_list:
        this_url_num = url.split('/')[-2]

        #2.发送网络请求（获得完整html代码）

        html_data = getresponse(isproxy,url,http_proxy,https_proxy)
        if html_data != '0':
            html_data_text = html_data.text
            print('正在处理：',url)
            #print(html_data_text) 用于返回状态码
            selector=parsel.Selector(html_data_text)

            #额外步骤获取作者的id
            try:
                author_list = selector.xpath("//div[@class='items_article_headerInfo']/ul/li[3]/a/text()").getall()
                author = author_list[0]
            except:
                author = 'unknown'
                
            #4.筛选目标信息（是否存在预览图片，是则保存图片数量、图片链接，否则返回nodata）
            if isdown_bigpic =='yes':
            #预览原图（清晰，体积大）
                fc2_pic_list = selector.xpath("//ul[@class ='items_article_SampleImagesArea']/li/a/@href").getall()
            else:
            #缩略版预览图（较模糊，体积小）
                fc2_pic_list = selector.xpath("//ul[@class ='items_article_SampleImagesArea']/li/a/img/@src").getall()
            print('当前资源的作者ID：%s' % author)
            if fc2_pic_list != []:
                #5.逐一访问图片链接并按（fc2番号_图片序号）保存目标信息为jpg，保存到pic文件夹
                threads = []
                print('找到的预览图片共%s张' % len(fc2_pic_list))
                for i in range(0,len(fc2_pic_list)):
                    if isdown_bigpic == 'yes':
                        pic_url = fc2_pic_list[i]
                    else:
                        pic_url = 'https:' + fc2_pic_list[i]
                    try:
                        thread = Download_Thread(i,this_url_num,isproxy,pic_url,http_proxy,https_proxy,i)
                        thread.start()
                        threads.append(thread)
                    except:
                        print ("Error: 无法启动线程")
                if threads != []:        
                    for t in threads:
                        t.join()                    
            else:
                print('当前资源没有预览图')
            time.sleep(1)

            #设置休眠，防止被服务器拒绝
            tiktok=tiktok + 1
            if tiktok > 5:
                print('休眠5s中，防止服务器拒绝')
                time.sleep(5)
                tiktok = 0

            #每下载20个资源的预览图片，保存一次数据
            sum += 1
            if sum > 20 :
                all_df.to_excel(filename,index=False)
                sum = 0
            
    all_df.to_excel(filename,index=False)

def findnumbyAuthor():
    link = input('输入作者主页：')

    #格式化config选项
    getconfig = Config.Config()
    isproxy = getconfig.isproxy
    http_proxy = getconfig.http_proxy
    https_proxy = getconfig.https_proxy
    getconfig.printconfig()

    fc2_data = pd.DataFrame(columns=['num','author','title','magnet','size','uploadtime'])
    isnextpage =True
    global author_name
    #resource_data=
    print(f'finding in {link}')
    while isnextpage:
        getsoures = getresponse(isproxy,link,http_proxy,https_proxy)
        if getsoures != 0:
            html_data = getsoures.text
            selector = parsel.Selector(html_data)
            num_data = selector.xpath('//a[@class="c-cntCard-110-f_itemName"]/@href').getall()
            title_data = selector.xpath('//a[@class="c-cntCard-110-f_itemName"]/@title').getall()
            auther_data = selector.xpath('//span[@class="c-cntCard-110-f_seller"]/a/text()').getall()
            for i in range(0,len(num_data)):
                carddata = {'num':num_data[i].split('=')[-1],'author':auther_data[i],'title':title_data[i],'magnet':'0&nothing','size':0,'uploadtime':000000}
                fc2_data = fc2_data.append(carddata,ignore_index=True)
                author_name = auther_data[i]
            #查询是否存在下一页，有则循环获取数据
            pagelink_list = selector.xpath("//div[@class='c-pager-101']/a/text()").getall()
            if len(pagelink_list)>0 and ' ›' in pagelink_list[-1]:
                getnextlink = selector.xpath('//div[@class="c-pager-101"]/a[last()]/@href').getall()
                link = getnextlink[0]
                print(f'finding in {link}')
            else:
                isnextpage = False
        else:
            print('link error!\ntry again after 1s')
            time.sleep(1)
            continue

    filename = f'./data/{auther_data[0]}.xlsx'
    fc2_data.to_excel(filename,index=False)

def FmagnetbyUID(author = ''):
    if author == '':
        author = input('输入作者名：')
    filename = f'./data/{author}.xlsx'
    print(filename)
    try:
        alldata = pd.read_excel(filename)

        #查找需要获取磁链的数据，合并到data变量中，以免提前更改本地数据的完整性
        data1 = alldata.loc[(alldata['magnet'] == '0&nothing')]
        #print(data1)
        data2 = alldata.loc[(alldata['magnet'] == 'no magnet')]
        data3 = alldata.loc[(alldata['magnet'] == '服务器拒绝访问')]
        data = pd.DataFrame(columns=['num','title','magnet','size','uploadtime','author'])
        data = data.append(data1)
        data = data.append(data2)
        data = data.append(data3)
        # print(data)

        #格式化config选项
        getconfig = Config.Config()
        isproxy = getconfig.isproxy
        http_proxy = getconfig.http_proxy
        https_proxy = getconfig.https_proxy
        getconfig.printconfig()


        for num in data['num']:
            link = f'https://sukebei.nyaa.si/?f=0&c=0_0&q={num}'
            getsoures = getresponse(isproxy,link,http_proxy,https_proxy)
            if getsoures != 0 :
                html_data = getsoures.text
                selector = parsel.Selector(html_data)
                magnet = selector.xpath('//tbody/tr/td[3]/a[2]/@href').getall()
                if magnet != []:
                    #print(magnet[0])
                    data.loc[data['num'] == int(num),['magnet']] = magnet[0]
                    size_data = selector.xpath('//tbody/tr/td[4]/text()').getall()
                    uploadtime_data = selector.xpath('//tbody/tr/td[5]/text()').getall()
                    data.loc[data['num'] == int(num),['size']] = size_data[0]
                    data.loc[data['num'] == int(num),['uploadtime']] = uploadtime_data[0]
                    print(f'{num}链接成功，且存在磁链')
                else:
                    data.loc[data['num'] == int(num),['magnet']] = 'no magnet'  
                    print(f'{num}链接成功，没有磁链')  
            else:
                data.loc[data['num'] == int(num),['magnet']] = '服务器拒绝访问'
                print(f'{num}链接失败，可能存在磁链')
            data.to_excel(filename,index=False)
            time.sleep(1)

    except:
        print('没有这个作者的信息，请先获取作者作品信息')
        
            
def main():
    warnings.filterwarnings("ignore")       #忽略ssl认证警告
    info = '''
    1.获取作者信息页
    2.获取作品磁链
    3.获取作品预览图
    4.获取作者作品页并搜索对应磁链
    '''
    global author_name
    go = '0'
    #print(info)
    while go == '1' or go == '2' or go == '3' or go == '4' or go == '0':
        os.system('cls')
        go = input(info)
        if go == '1':
            os.system('cls')
            findnumbyAuthor()
        elif go == '2':
            os.system('cls')
            FmagnetbyUID()
        elif go == '3':
            os.system('cls')
            getpic()
        elif go == '4':
            os.system('cls')
            findnumbyAuthor()
            FmagnetbyUID(author_name)


if __name__ == '__main__':
    main()