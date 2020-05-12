#-*- coding:utf-8 -*-
# @Author : Dummerfu
# @Time : 2020/4/26 18:17
import requests
import json
import time
import os
from pyecharts.charts import Bar,Line,Timeline
from pyecharts import options as opts
import pandas as pd
from progressbar import ProgressBar
import nameMap

dic={}
class Province(object):
    def __init__(self):
        self.num=''
        self.name=''
        self.confirm=[]
        self.confirmadd=[]
        self.heal=[]
        self.dead=[]
        self.timedata=[]
    def get_data(self,num,name):
        self.num=num
        self.name=name
        url = 'https://api.inews.qq.com/newsqa/v1/query/pubished/daily/list?province=' + name
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'}
        res = requests.get(url, headers=header)
        res.encoding = 'utf-8'
        res = json.loads(res.text)
        for daydata in res['data']:
            self.confirmadd.append(daydata['confirm_add'])
            self.confirm.append(daydata['confirm'])
            self.heal.append(daydata['heal'])
            self.dead.append(daydata['dead'])
            self.timedata.append(daydata['date'])
    def print_bar(self):
        bar = Bar(init_opts=opts.InitOpts(width='1080px',height='480px'))
        bar.add_xaxis(self.timedata)
        # category 是同系列直接的距离，gap是不同系列之间的距离
        bar.add_yaxis('治愈人数', self.heal,gap='100%',label_opts=opts.LabelOpts(is_show=False),itemstyle_opts=opts.ItemStyleOpts(color='#90EE90'))
        if self.name=='湖北':
            bar.add_yaxis('死亡人数', self.dead,gap='100%',label_opts=opts.LabelOpts(is_show=False),itemstyle_opts=opts.ItemStyleOpts(color='#696969'))
        # 设置全局变量：x轴标签倾斜度，html主标题
        bar.set_global_opts(datazoom_opts=[opts.DataZoomOpts(),opts.DataZoomOpts(type_='inside')],toolbox_opts=opts.ToolboxOpts(),xaxis_opts=opts.AxisOpts(name_rotate=-15),title_opts=opts.TitleOpts(self.name, subtitle='数据来自inews'))
        line=Line()
        line.add_xaxis(self.timedata)
        line.add_yaxis('确诊人数', self.confirm,label_opts=opts.LabelOpts(is_show=False), itemstyle_opts=opts.ItemStyleOpts(color='#F08080'))
        print(self.name+'.html','已成功生成到',os.getcwd())
        # 在bar的基础上画line
        bar.overlap(line).render(self.name+'.html')
def output_to_data_frame(all_province_name):
    confirm_alllist=[]
    timelist=[]
    leng=len(all_province_name)
    pgb=ProgressBar().start()
    print('请等待...')
    for i,pr in enumerate(all_province_name):
        # 自动是key值
        time.sleep(0.01)
        pgb.update(int(i/(leng-1)*100))
        province[i].get_data(i,pr)
        dic[pr]=i
        # 找共同的时间序列 所以不需要再转excel自动补全了 缺点就是数据量减少了
        if len(timelist)>len(province[i].timedata) or len(timelist)==0:
            timelist=province[i].timedata
    l=len(timelist)
    for i,pr in enumerate(all_province_name):
        confirm_alllist.append(province[i].confirm[-l:])

    confirm_frame = pd.DataFrame(confirm_alllist)
    pgb.finish()
    os.system('cls')
    return confirm_frame,timelist
def get_province():
    all_province=[]
    for i in nameMap.city_name_map:
        all_province.append(i)
    return all_province
def get_Top10info(province_name,day):
    heal_list=[]
    dead_list=[]
    for name in province_name:
        heal_list.append(province[dic[name]].heal[-day])
        dead_list.append(province[dic[name]].dead[-day])
    return heal_list,dead_list
def print_bar(confirm_frame,timelist,all_province_name):
    tl=Timeline(init_opts=opts.InitOpts(page_title='疫情可视化',width='1080px',height='480px'))
    # 调节播放速率 ,是否自动播放，是否循环播放，是否显示时间轴
    tl.add_schema(play_interval=300,is_auto_play=True,is_loop_play=False,is_timeline_show=True)
    l=len(timelist)
    for i in range(0,l):
        # 将每天的数据单独拿出来进行排序
        s = {'province': all_province_name, 'confirm': confirm_frame.loc[:][i]}
        s = pd.DataFrame(s)
        # 翻转是镜像翻转所以 这里要从大到小排序
        s = s.sort_values(by='confirm', ascending=1)
        province_name=s[-10:]['province']
        confirm=s[-10:]['confirm']
        heal_list,dead_list=get_Top10info(province_name,l-i)
        bar = Bar()
        bar.add_xaxis(province_name .to_list())
        # 名字，数据，柱状图间距， label标签显示在右侧|这样翻转的时候就在右侧
        # gap 神奇的参数因为每个柱状图有固定位置|宽度l， 正代表向正向移动百分比l，负代表向负向移动百分比l
        bar.add_yaxis('确诊人数',confirm.to_list(),label_opts=opts.LabelOpts(position='right'),color='#696969')
        bar.add_yaxis('治愈人数',heal_list,label_opts=opts.LabelOpts(position='right'),color='#90EE90')
        bar.add_yaxis('死亡人数', dead_list,label_opts=opts.LabelOpts(position='right'),color='#F08080')
        # 设置全局变量：x轴标签倾斜度，html主标题
        bar.set_global_opts(legend_opts=opts.LegendOpts(is_show=True),xaxis_opts=opts.AxisOpts(name_rotate=-15),title_opts=opts.TitleOpts('当前日期：%s'%timelist[i],subtitle='数据来自inews'))
        bar.reversal_axis()
        tl.add(bar,timelist[i])
    name='疫情柱状图.html'
    print(name,'已成功生成到',os.getcwd())
    tl.render(name)
def output_file(confirm_frame,timelist):
    confirm_frame.to_excel('疫情数据.xls',header=timelist,index=all_province_name)
    print('疫情数据.xls已成功生成到',os.getcwd())
    pass
if __name__=='__main__':
    os.system('cls')
    all_province_name=get_province()
    province=[Province() for i in range(1000)]
    confirm_frame,timelist=output_to_data_frame(all_province_name)
    print('退出程序后才会出现生成的文件')
    while 1:
        print('         输入指令all : 生成一个所有省的动态排名柱状图\n'
              '                 get :生成一个所有省的excel疫情数据\n'
              '                 省份的名称:生成一个该省的疫情数据图\n'
              '                 return :退出程序\n'        
              '                 (指令不包含冒号|空格)')
        word=input('请输入指令...')
        if word=='all':
            print_bar(confirm_frame,timelist,all_province_name)
        if word=='return':
            print('已完成')
            exit(0)
        if word=='get':
            output_file(confirm_frame,timelist)
        if word in all_province_name:
            province[dic[word]].print_bar()
        time.sleep(3)
        os.system('cls')
