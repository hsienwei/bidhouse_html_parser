# coding=utf8

import mechanize

'''
#法拍屋查詢入口
url = "http://aomp.judicial.gov.tw/abbs/wkw/WHD2A00.jsp"

br = mechanize.Browser()
br.set_handle_robots(False) # ignore robots
br.open(url)

#地區選擇

#for form in br.forms():
#    print form

#print court_control.items
br.select_form(name="form")
court_control = br.form.find_control("court")
#for court in court_control.items:
#    court_value = court.attrs['value']
#    print "地方:" + court_value
br['court'] = ['PCD']#[court_value]
br.submit()
#    br.back();
#content = res.read()
#with open("mechanize_results.html", "w") as f:
#	f.write(content)
#
#屋型選擇
br.select_form(name="form")
#for form in br.forms():
#	print form
br['saletype'] = ['1']
br['proptype'] = ['C52']
br.submit()

#細部條件篩選(選全部)
br.select_form(name="form")
#form.set_value(["hsimun"], kind="singlelist", nr=0)
hsimun_control = br.form.find_control("hsimun")
ctmd_control = br.form.find_control("ctmd")
sec_control = br.form.find_control("sec")
#print "------------------"
for control in br.form.controls:
    print control
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
#content = res.read()
#with open("mechanize_results.html", "w") as f:
#    f.write(content)

br.select_form(name="form")
#for form in br.forms():
#    print form

#取得該類別總頁數與每頁筆數
page_count = br.form.find_control("pageTotal").value
record_per_page = br.form.find_control("pageSize").value

#print page_count
#print record_per_page

for i in  range( 1, int(page_count) + 1 ):
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
    with open("mechanize_results" + str(i) + ".html", "w") as f:
        f.write(content)
    br.back()
'''        

#======================================================
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
    #content = res.read()
    #with open("mechanize_results.html", "w") as f:
    #    f.write(content)
    
    br.select_form(name="form")
    #for form in br.forms():
    #    print form
    
    #取得該類別總頁數與每頁筆數
    page_count = br.form.find_control("pageTotal").value
    record_per_page = br.form.find_control("pageSize").value
    print "Page:" + str(page_count) + ", record per page " +  str(record_per_page)
    #print page_count
    #print record_per_page
    catchAllPage( br, page_count)
    
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


def dataCollect():
    br = initBrowser()
    locationSelect(br)
    

if __name__ == "__main__":
    dataCollect();
