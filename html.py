# coding=utf8

import mechanize
from bs4 import BeautifulSoup, Tag

def initBrowser():
    url = "http://aomp.judicial.gov.tw/abbs/wkw/WHD2A00.jsp"
    br = mechanize.Browser()
    br.set_handle_robots(False) # ignore robots
    br.open(url)
    return br

def locationSelect( br ):
    br.select_form(name="form")
    court_control = br.form.find_control("court")

    for court in court_control.items:
        br.select_form(name="form")
        #court_control = br.form.find_control("court")
        court_value = court.attrs['value']
        print "location:" + court_value
        br['court'] = [court_value]
        br.submit()
        typeSelect( br )
        br.back()

def typeSelect( br ):        
    #屋型選擇
    br.select_form(name="form")
    #for form in br.forms():
    #   print form
    br['saletype'] = ['1']
    br['proptype'] = ['C52']
    br.submit()
    detailSelect( br )
    br.back()

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
    #catchAllPage( br, page_count)
    
    br.back()   

def catchAllPage( br, page_count):
    for i in  range( 1, int(page_count) + 1 ):
        print "get page" + str(i)
        br.select_form(name="form")
        page_str = str(i)
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
        #with open("mechanize_results" + str(i) + ".html", "w") as f:
        #    f.write(content)
        br.back()


def soupTest():
    soup = BeautifulSoup(open("mechanize_results1.html"))
    tag = soup.table
   
    tr_title = None

    #找資料表格title <tr>
    tablelist = soup.find_all("tr")    
    for tr_data in  tablelist:
        if not (tr_data.td.div is None):
            for str in tr_data.td.div.stripped_strings:
                if repr(str) == repr(u"筆次"):
                    tr_title = tr_data
                    break
        if not tr_title is None:
            break

    #以表格title找兄弟<tr>       
    if not tr_title is None:
        for sibling in tr_title.next_siblings:
            if type(sibling) is Tag:
                parseRecord(sibling)

#用資料<tr>取其中的<td>
def parseRecord(record_tr_tag):
    print "==============================="
    #print record_tr_tag
    td_list = record_tr_tag.find_all('td')
    print len(td_list)
    i = 0
    data_list = {}
    for td in td_list:
        print "---"
        #print i
        print td
        print len(list(td.descendants))
        combine_str = ""
        for string in td.stripped_strings:
            print type(string)
            combine_str = combine_str + repr(string)
        data_list[i] = combine_str
        print "< < " + combine_str
        i = i + 1
    print data_list
    print "^^"
    for a in data_list:
        print type(data_list[a])
        print data_list[a]
        print data_list[a].encode('utf8')

def dataCollect():
    br = initBrowser()
    locationSelect(br)
    

if __name__ == "__main__":
    #dataCollect();
    soupTest()
