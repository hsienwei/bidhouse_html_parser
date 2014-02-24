# coding=utf8

import mechanize
from bs4 import BeautifulSoup, Tag
import re
import json
import os
import zipfile, os 
import hashlib
from functools import partial

def initBrowser():
    url = "http://aomp.judicial.gov.tw/abbs/wkw/WHD2A00.jsp"
    br = mechanize.Browser()
    br.set_handle_robots(False) # ignore robots
    br.open(url)
    return br

def locationSelect( br ):
    global curLocation
    br.select_form(name="form")
    court_control = br.form.find_control("court")

    for court in court_control.items:
        br.select_form(name="form")
        #court_control = br.form.find_control("court")
        court_value = court.attrs['value']
        print "location:" + court_value
        br['court'] = [court_value]
        curLocation = court_value

        br.submit()
        typeSelect( br )
        br.back()

def typeSelect( br ):    
    global curSaleType    
    saleType = ['1', '4']

    for stype in saleType:
        curSaleType = stype
        #屋型選擇
        br.select_form(name="form")
        #for form in br.forms():
        #   print form
        br['saletype'] = [stype]   #1一般程序 4應買公告 5拍定價格
        br['proptype'] = ['C52'] #C52房屋 C51土地 C54動產

        br.submit()
        detailSelect( br )
        br.back()
        '''
        jsonStr = json.dumps(totalAry, indent=4)
        with open(curLocation + "_" + ".html", "w") as f:
            f.write(jsonStr)
            '''

def detailSelect( br ):
    #細部條件篩選(選全部)
    br.select_form(name="form")
    #form.set_value(["hsimun"], kind="singlelist", nr=0)
    hsimun_control = br.form.find_control("hsimun")
    ctmd_control = br.form.find_control("ctmd")
    sec_control = br.form.find_control("sec")
    #print "------------------"
    #for control in br.form.controls:
    #    print control
    mechanize.Item(hsimun_control, {"contents": "全部","value": "all"})
    mechanize.Item(ctmd_control, {"contents": "全部","value": "all"})
    mechanize.Item(sec_control, {"contents": "全部","value": "all"})
    #print "------------------"    
    #print br.form
    #for form in br.forms():
    #    print form
    br['hsimun'] = ['all']
    br['ctmd'] = ['all']
    br['sec'] = ['all']
    br.submit()
    
    
    br.select_form(name="form")
    #for form in br.forms():
    #    print form
    
    #取得該類別總頁數與每頁筆數
    page_count = br.form.find_control("pageTotal").value
    record_per_page = br.form.find_control("pageSize").value
    print "Page:" + str(page_count) + ", record per page " +  str(record_per_page)
    #print page_count
    #print record_per_page
    allAry = catchAllPage( br, page_count)
    jsonStr = json.dumps(allAry, indent=4)
    with open(curLocation + "_" + curSaleType + ".json", "w") as f:
        f.write(jsonStr)
    jsonList.append(curLocation + "_" + curSaleType + ".json")        
    br.back()   

def catchAllPage( br, page_count):
    totalAry = [];
    global curPage
    for i in  range( 1, int(page_count) + 1 ):
        print "get page" + str(i)
        br.select_form(name="form")
        page_str = str(i)
        curPage =  page_str
        #print page_str
        #print type(page_str)
        page_control = br.form.find_control("pageNow")
        page_control.readonly = False
        page_control.value = page_str
        #mechanize.Item(page_control, {"contents": "全部","value": page_str})
        #form.set_value_by_label(['1'], "pageNow")
        #print page_control
        #br['pageNow'] = ['1']
        res = br.submit()
        content = res.read()
        subAry = htmlParse(content)
        totalAry = totalAry + subAry
        #with open(curLocation + "_" + str(i) + ".html", "w") as f:
        #    f.write(content)
        br.back()
    return totalAry    

def htmlParse(data):
    with open( curLocation + "_" + curSaleType  + "_" + curPage + ".html", "w") as f:
        f.write(data) 

    soup = BeautifulSoup(data,  features="html5lib")
    tag = soup.table
   
    tr_title = None

    #找資料表格title <tr>
    tablelist = soup.find_all("tr")    
    # old
    for tr_data in  tablelist:
        if not (tr_data.td.div is None):
            for str in tr_data.td.div.stripped_strings:
                if repr(str) == repr(u"筆次"):
                    tr_title = tr_data
                    print '有找到筆次'
                    break   
        if not tr_title is None:
            break
    '''
    for tr_data in  tablelist:
        tdlist = tr_data.find_all("td")    
        for td_data in  tdlist:
            divlist = td_data.find_all("div")  ## TODO  not use find_all
            for div_data in  divlist: 
                if not div_data.string is None:
                    for str in div_data.stripped_strings:
                        print str.encode('utf8')
                        if repr(str) == repr(u"筆次"):
                            tr_title = tr_data
                            print '有找到筆次'
                            print div_data
                            print tr_data
                            print tr_title
                            break
                        if not tr_title is None:
                            break    
                if not tr_title is None:
                    break                
            if not tr_title is None:
                break            
        if not tr_title is None:
            break                
    '''         

    ary = []
    #以表格title找兄弟<tr>       
    if not tr_title is None:
        #print tr_title
        for sibling in tr_title.next_siblings:
            if type(sibling) is Tag:
                #print sibling
                ary.append(parseRecord(sibling))
    else:
        print '沒找到筆次' 
        if os.path.exists(curLocation + "_" + curSaleType  + "_" + curPage + ".err"):
            os.remove(curLocation + "_" + curSaleType  + "_" + curPage + ".err")
        with open( curLocation + "_" + curSaleType  + "_" + curPage + ".err", "w+") as f:
            for tr_data in  tablelist:
                if not (tr_data.td.div is None):
                    for str in tr_data.td.div.stripped_strings:
                        f.write(str.encode('utf8'))    
                        f.write('\n==========================================================\n')          
    return ary            

#用資料<tr>取其中的<td>
def parseRecord(record_tr_tag):
    #print "==============================="
    #print record_tr_tag
    td_list = record_tr_tag.find_all('td')
    ##print len(td_list)
    i = 0
    data_list = {}
    for td in td_list:
        data_list = dict(data_list.items() + parseTd(td, i).items())
        i = i + 1
    return data_list

def parseTd(td, index):
    ##print "==================="
    ##print td
    ##print "==================="
    combine_str = getTdStr(td)
    simpleStr = getCleanStr(combine_str) 
    ##print simpleStr

    rtn = {}
    if index == 0: #為 IDX 
        print simpleStr
    elif index == 1: ##字號股別 done
        rtn['word'] = simpleStr
        
    elif index == 2: ##拍賣日期 拍賣次數  example: 103/01/15第2拍 done
        m = re.search('([0-9/]+)(.+)', simpleStr)
        rtn['sale_date'] = m.groups()[0]
        rtn['sale_round'] = m.groups()[1] 
        #print m.groups()[1] 
    elif index == 3: ##縣市
        rtn['county'] = simpleStr   
    elif index == 4: ##房屋地址/樓層面積  & 公告 &持分 & 坪數 &底價 done
        ## example: 新北市三重區安慶街152號3樓14坪x6分之1建物拍賣底價:新台幣60,000元
        m = re.search('(.+?)([0-9]+)坪x(.+)建物拍賣底價:新台幣([0-9,]+)元', simpleStr)
        rtn['address'] = m.groups()[0]
        rtn['ping'] = m.groups()[1]
        rtn['part'] = m.groups()[2]
        rtn['reserve_price'] = m.groups()[3]
        ## get post
        rtn['post'] = td.a["href"]
    elif index == 5: ## 5 總拍賣底價(元)  done
        rtn['total_reserve_price'] = int(getPureNumberStr(simpleStr)) 
    elif index == 6: ##6 點交       
        rtn['handover'] = simpleStr
    elif index == 7: ##7 空屋
        rtn['empty_house'] = simpleStr
    elif index == 8: ##8 標 別
        rtn['sale_type'] = simpleStr
    elif index == 9: ##9 備 註
        rtn['remark'] = simpleStr   
        if not td.a is None:
            rtn['remark_link'] = td.a["href"]
    elif index == 11: ##11採通訊投標
        rtn['communication'] = simpleStr
        '''
    else: ##    10 看圖  12土地有無遭受污染 
        print 'pass'
        '''
    return rtn  

def getTdStr(td):
    combine_str = u""
    for string in td.stripped_strings:
        combine_str = combine_str + string
    return combine_str

def getCleanStr(uStr):
    cstr = uStr.encode('utf8').replace(" ", "") 
    cstr = cstr.replace("　", "") 
    cstr = cstr.replace(" ", "") 
    cstr = cstr.replace("\n", "") 
    return cstr

def getPureNumberStr(uStr):    
    cstr = uStr.encode('utf8').replace(",", "") 
    return cstr

def printCleanStr(uStr):
    print getCleanStr(uStr)

def dataCollect():
    
    global jsonList
    jsonList = []

    br = initBrowser()
    locationSelect(br)

    # zip all data
    with zipfile.ZipFile('data.zip', 'w', zipfile.ZIP_DEFLATED) as myzip:
        for jsonFile in jsonList:
            myzip.write(jsonFile)

    # gen md5      
    with open('data.zip', mode='rb') as f:
        m = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            m.update(buf)
  
        with open( "md5.txt", "w") as f:
            f.write(m.hexdigest())   

if __name__ == "__main__":
    dataCollect();
    
