#!/usr/bin/env python
# coding: utf-8

# In[2]:


from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4, inch
from reportlab.platypus import Image, Paragraph,LongTable, SimpleDocTemplate,Frame, Table, PageBreak, KeepInFrame,Spacer, KeepTogether 
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import simpleSplit
from bs4 import BeautifulSoup
import urllib
import requests
from urllib.request import urlopen,Request
import bs4
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from selenium.webdriver.common.by import By
import time
import xlsxwriter
from PyPDF2 import PdfFileMerger, PdfFileReader
from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

# In[5]:


class lawScrapper:
    pageNum=0
    path=r"C:\Users\DELL Precision 7510\Documents\EU laws\\"
    url=""
    lang=""
    engTitle=""
    otherTitle=""
    coverSubTitle=[]
    coverTitle=[]
    articleNum=[]
    docName=""
    resultsNum=0
    topTitle="Recitals"
    currentBookNum=0
    styles = getSampleStyleSheet()
    port = 465  # For SSL
    excelNum=0
    smtp_server = "smtp.gmail.com"
    sender_email = "ChantHeiko@gmail.com"  # Enter your address
    receiver_email = "joulfaian8@gmail.com"  # Enter receiver address
    password = "ChantHeiko1234"
    styleA = styles["BodyText"]
    styleA.fontName = "SEGOEUI"
    styleA.fontSize = 10
    styleA.alignment=TA_JUSTIFY
    styleA.spaceAfter = 9
    styleA.wordWrap=1
    styleA.spaceShrinkage = 0.02
    styleA.allowOrphans: 1
    styleAB = styles["Normal"]
    styleAB.fontName = "SEGOEUIB"
    styleAB.fontSize = 10
    styleAB.alignment=TA_JUSTIFY
    styleAB.spaceAfter = 9
    styleAB.wordWrap=1
    styleAB.spaceShrinkage = 0.02
    styleAB.allowOrphans: 1
    excelNum=1
    styles.add (ParagraphStyle('coverSubTitle',
                               fontName="SegoeUI",
                               textColor="#003060",
                               fontSize=9, alignment=TA_JUSTIFY))
    styles.add (ParagraphStyle('coverTitle',
                               fontName="SegoeUI",
                               textColor="#FFFFFF",
                               fontSize=10, alignment=TA_JUSTIFY))
    styles.add (ParagraphStyle('firstPageTitle',
                               fontName="SegoeUI",
                               textColor="#000000",
                               fontSize=10, alignment=TA_JUSTIFY))
    
    def __init__(self):
        pdfmetrics.registerFont(TTFont('SegoeUI', self.path+"segoe-ui\SEGOEUI.TTF"))
        pdfmetrics.registerFont(TTFont('SegoeUIB', self.path+"segoe-ui\SEGOEUIB.TTF"))

        
    def Start(self):
        driver = webdriver.Chrome(self.path+"chromedriver")
        driver.get("https://eur-lex.europa.eu/homepage.html")
        a=driver.find_element_by_xpath("//a[text()='Legal acts']")
        driver.execute_script("arguments[0].click();", a)
        a=driver.find_element_by_xpath("//a[text()='Search in legal acts']")
        driver.execute_script("arguments[0].click();", a)
        driver.find_element_by_xpath("//input[@id='legInForce']").click()
        driver.find_element_by_xpath("//input[@id='excCorr']").click()
        driver.find_element_by_xpath("//input[@id='typeOfActStatusRegulation']").click()
        driver.find_element_by_xpath("//input[@id='topSearch']").click()
        self.resultsNum=int(driver.find_elements_by_tag_name("strong")[5].text)
        a=driver.find_element_by_xpath("//a[@id='cellar_5231605d-8dd5-11eb-b85c-01aa75ed71a1']")
        driver.execute_script("arguments[0].click();", a)
        time.sleep(5) 
        select = Select(driver.find_element_by_id('MDLang2'))
        select.select_by_index(1)
        a=driver.find_element_by_xpath("//button[text()='Display']")
        driver.execute_script("arguments[0].click();", a)
        Errorkbook = xlsxwriter.Workbook(self.path+'excel\\Errors.xlsx')
        errorsheet = Errorkbook.add_worksheet()
        errorRow=1
        errorsheet.write(0,0,"Doc Number")
        errorsheet.write(0,1,"Languages")
        errorsheet.write(0,2,"Reason")
        for i in range(1,self.resultsNum+1):
            try:
                select = Select(driver.find_element_by_id('MDLang2'))
                for j in range(0,len(select.options)):
                    try:
                        if self.currentBookNum%100==0:
                            print("creating excel number:" + str(self.excelNum)) 
                            workbook = xlsxwriter.Workbook(self.path+'excel\\'+str(self.excelNum)+'.xlsx')
                            worksheet = workbook.add_worksheet()
                            columnNames=['Interior File Path','Cover File Path','Title','Subtitle','Author - Prefix','Author - First Name','Author - Middle Name','Author - Last Name','Author - Suffix', 'Description','Keyword #1','Keyword #2','Keyword #3','Keyword #4','Keyword #5','Keyword #6','Keyword #7','Price','Category #1','Category #2','Primary Marketplace','Expanded Distribution', 'Round Price To#.99 After VAT' ]
                            col=0
                            for item in columnNames:
                                worksheet.write(0,col,item)
                                col+=1
                        select = Select(driver.find_element_by_id('MDLang2'))
                        select.select_by_index(j)
                        selected_option = select.first_selected_option
                        self.lang=selected_option.text.split(" ")[0]
                        self.articleNum=[]
                        self.engTitle=""
                        self.otherTitle=""
                        self.coverSubTitle=[]
                        self.coverTitle=[]
                        self.topTitle="Recitals"
                        if self.lang!="English":
                            a=driver.find_element_by_xpath("//button[text()='Display']")
                            driver.execute_script("arguments[0].click();", a)
                            result,message=self.getStarted(driver) 
                            if result==True:
                                self.currentBookNum+=1
                                self.addRowtoExcel(worksheet)
                                print(self.currentBookNum, self.currentBookNum%100, self.currentBookNum%100==0)
                                if self.currentBookNum%100==0:
                                    print("Closing the Excel and sending an email ...")
                                    workbook.close()
                                    self.sendEmail("Excel","Excel number {} is ready to be uploaded.".format(str(self.excelNum)))
                                    self.excelNum+=1
                            else:
                                errorsheet.write(errorRow,0,self.docName)
                                errorsheet.write(errorRow,1,"English -"+self.lang)
                                errorsheet.write(errorRow,2,str(message))
                                errorRow+=1
                                
                    except Exception as e:
                        text="""{} after English - {} failed to be published, because of the following exception error:\n
                    {}""".format(self.docName,self.lang, str(e))
                        self.sendEmail("EXCEPTION ERROR",str(e))
                        
                a=driver.find_element_by_xpath("//span[text()='Next']")
                driver.execute_script("arguments[0].click();", a)


            except Exception as e:
                self.sendEmail("EXCEPTION ERROR",str(e))
                Errorkbook.close()
                break

        self.sendEmail("Success","Done downloading the books")
                
         
            
    
    def getStarted(self, driver):
        page_soup = BeautifulSoup(driver.page_source, "html.parser")
        self.docName=page_soup.findAll('h1',{"class":"DocumentTitle"})[0].getText().replace(u'\xa0', u' ')
        found= page_soup.findAll("table",{"class":"table-responsive"})
        result,message=self.createPDF(found)
        return (result,message)
    
    def addRowtoExcel(self, worksheet):
        Description="""<h1>European Union Law - The Bilingual Editions</h1>
<p>We have 24 official languages in the European Union. English remains an official EU language even after Brexit.</p>
<p>European legislation is subject to interpretation. Due to the variety of language versions, there are a number of linguistic differences. The book series "European Union Law - The Bilingual Editions" intends to allow multiple linguistic versions to be used for interpretation.</p>
<p>Therefore, in our book series, the English legal texts are published in addition to a second language version to enable a simple comparison of European legal provisions and make interpretation easier.</p>"""
        worksheet.write(((self.currentBookNum-1)%100+1),0,self.path+"files\\"+self.docName+"English-"+self.lang+".pdf" )
        worksheet.write(((self.currentBookNum-1)%100+1),1,self.path+"covers\\"+self.docName+"English-"+self.lang+".pdf" )
        worksheet.write(((self.currentBookNum-1)%100+1),2,"English - "+self.lang+" | "+self.coverTitle[0]+" "+self.coverTitle[2] )
        worksheet.write(((self.currentBookNum-1)%100+1),3,"English - "+self.lang+" | "+self.coverTitle[1]+" "+self.coverTitle[3] )
        worksheet.write(((self.currentBookNum-1)%100+1),5,"Heiko" )
        worksheet.write(((self.currentBookNum-1)%100+1),6,"Jonny" )
        worksheet.write(((self.currentBookNum-1)%100+1),7,"Maniero" )
        worksheet.write(((self.currentBookNum-1)%100+1),9,Description )
        worksheet.write(((self.currentBookNum-1)%100+1),10,"EU Directive" )
        worksheet.write(((self.currentBookNum-1)%100+1),11,"European Union Law" )
        worksheet.write(((self.currentBookNum-1)%100+1),12,"EU Legislation")
        worksheet.write(((self.currentBookNum-1)%100+1),13,"EU Regulation" )
        worksheet.write(((self.currentBookNum-1)%100+1),14,"European law" )
        worksheet.write(((self.currentBookNum-1)%100+1),15,"EU law" )
        worksheet.write(((self.currentBookNum-1)%100+1),16,"law" )
        worksheet.write(((self.currentBookNum-1)%100+1),17,"7,99" )
        worksheet.write(((self.currentBookNum-1)%100+1),18,"Nonfiction > Law > Civil Law" )
        worksheet.write(((self.currentBookNum-1)%100+1),19,"Nonfiction > Law > International" )
        worksheet.write(((self.currentBookNum-1)%100+1),20,"Amazon.de" )
        worksheet.write(((self.currentBookNum-1)%100+1),21,"YES" )
        worksheet.write(((self.currentBookNum-1)%100+1),22,"YES" )
        
    def sendEmail(self, subject,  text):
        message = MIMEMultipart("alternative")
        message["From"] = "ChantHeiko@gmail.com"
        message["To"] = "joulfaian8@gmail.com"
        message["CC"] = "info@willing-able.com" if subject=="Excel" else ""
        message["Subject"] = subject
        message.Subject = subject
        part1 = MIMEText(text, "plain")
        message.attach(part1)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, [self.receiver_email]+[message["CC"]], message.as_string())
            
            
    def getData(self, found):
        data=[]
        j=1
        if found is None or len(found)==0:
            return ([], "no html table body")
        for line in found[0].findAll('tr'):
            row=[]
            i=1
            P0=[]
            engBold=False
            for l in line.findAll('td'):
                if j>=2 and j<=4:
                    if len(l.getText())>968:
                        return ([], "Title too long")
                    self.coverTitle.append(l.getText()) 
                elif j==1:
                    if len(l.getText())>76:
                        return ([], "SubTitle too long")
                    self.coverSubTitle.append(l.getText())         
                if engBold==True or len(l.getText().replace(u'\xa0', u' '))<20 and len(l.getText().replace(u'\xa0', u' ').split(" "))==2 and ((l.getText().replace(u'\xa0', u' ').split(" ")[0]=="Article"and l.getText().replace(u'\xa0', u' ').split(" ")[1].isdecimal()) or (l.getText().replace(u'\xa0', u' ').split(" ")[0]=="ANNEX" and l.getText().replace(u'\xa0', u' ').split(" ")[1].isalpha()) ):
                    engBold=True
                    P0 =Paragraph(l.getText(),self.styleAB)
                elif l.getText()=="For the European Parliament":
                    engBold=True
                    P0 =Paragraph(l.getText(),self.styleAB) 
                else:
                    P0 =Paragraph(l.getText(),self.styleA)
                row.append(P0)
            if row[0].text=='\xa0' or row[1].text=='\xa0':
                return ([], "Not Aligned")
            data.append(row)
            j+=1
        return (data, "")
    
    def addPageNumber(self,canvas, doc):
        self.pageNum = canvas.getPageNumber()
        text = "Page %s" % str(self.pageNum+2)
        topTitle=self.topTitle.split(", ")
        topTitle=topTitle[len(topTitle)-1]
        PresidenNameOccurs=False
        canvas.setLineWidth(3)
        text2=""
        topTitle2=""
        for item in self.articleNum:
            if item["pNum"]==self.pageNum:
                if item["name"]=="For the European Parliament":
                    topTitle=""
                    PresidenNameOccurs=True
                else:
                    topTitle2+=", "+item["name"] if topTitle2 else item["name"]
        canvas.setFont("Helvetica-Bold", 9)
        if self.pageNum%2==0:
            canvas.drawString(0.5*inch, 8.6*inch, topTitle2 or topTitle)
        else:
            canvas.drawRightString(5.5*inch, 8.6*inch, topTitle2 or topTitle)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawRightString(1*inch, 8.4*inch, "English")
        canvas.drawRightString(5.5*inch, 8.4*inch, self.lang)
        canvas.line(0.5*inch, 8.3*inch,5.5*inch, 8.3*inch)
        canvas.setFont("Helvetica", 10)
        canvas.drawRightString(5.5*inch, 0.3*inch, text)
        canvas.line(0.5*inch, 0.5*inch,5.5*inch, 0.5*inch)
        self.topTitle="" if PresidenNameOccurs==True else (topTitle2 or topTitle)
        
    def createFirstPage(self):
        c  = canvas.Canvas(self.path+'firstPage.pdf', pagesize=(6*inch, 9*inch))
        pages = PdfReader(self.path+'frames\\'+'Frame3.pdf').pages
        pages = [pagexobj(x) for x in pages]
        for page in pages:
            c.setPageSize((page.BBox[2], page.BBox[3]))
            c.doForm(makerl(c, page))

        c.setFillColorRGB(0/256,0/256,6/256)
        c.setFont("SegoeUI", 14)
        text = "English - "+self.lang+" - First Edition"
        c.drawCentredString(3*inch, 8*inch, text)

        p = Paragraph(self.engTitle, self.styles['firstPageTitle'])
        p.wrapOn(c,((454/96))*inch, 3*inch)
        p.drawOn(c, ((6-(453/96))/2)*inch, 4.1*inch)

        p = Paragraph(self.otherTitle, self.styles['firstPageTitle'])
        x,y=p.wrapOn(c,((454/96))*inch, 3*inch)
        p.drawOn(c,((6-(453/96))/2)*inch, 3.8*inch-y)
        c.save()
        M=PdfFileMerger()
        M.append(self.path+"firstPage.pdf")
        M.append(self.path+'frames\\'+"Frame54.pdf")
        M.write(self.path+"First2Pages.pdf")
        M.close()
        M=PdfFileMerger()
        M.append(self.path+"files\\"+self.docName+"English-"+self.lang+".pdf")
        M.write(self.path+"convert.pdf")
        M.close()
        M=PdfFileMerger()
        M.append(self.path+"First2Pages.pdf")
        M.append(self.path+"convert.pdf")
        M.write(self.path+"files/"+self.docName+"English-"+self.lang+".pdf")
        M.close()
        os.remove(self.path+"convert.pdf")
        os.remove(self.path+"firstPage.pdf")
        os.remove(self.path+"First2Pages.pdf")
        
    def addCover(self):
        w=12.25*inch+((self.pageNum+2)+(4-(self.pageNum+2)%4))* 0.002252*inch
        c  = canvas.Canvas(self.path+'covers\\'+self.docName+"English-"+self.lang+'.pdf', pagesize=(w, 9.25*inch))
        c.setFillColorRGB(228/256,240/256,255/256)
        c.rect(0*mm,0*inch,w,9.25*inch,stroke=0, fill=1)    
        c.setFillColorRGB(5/256,92/256,157/256)
        c.rect(0*mm,(121/96)*inch,w,(619/96)*inch,stroke=0, fill=1)

        if self.currentBookNum%400<101:
            pages = PdfReader(self.path+'frames\\'+'Frame13.pdf').pages
            pages = [pagexobj(x) for x in pages]
        elif self.currentBookNum%400<201:
            pages = PdfReader(self.path+'frames\\'+'Frame15.pdf').pages
            pages = [pagexobj(x) for x in pages]
        elif self.currentBookNum%400<301:
            pages = PdfReader(self.path+'frames\\'+'Frame16.pdf').pages
            pages = [pagexobj(x) for x in pages]
        else:
            pages = PdfReader(self.path+'frames\\'+'Frame17.pdf').pages
            pages = [pagexobj(x) for x in pages]

        pages1 = PdfReader(self.path+'frames\\'+'Frame9.pdf').pages
        pages1 = [pagexobj(x) for x in pages1]

        c.translate(0, 0)
        c.doForm(makerl(c, pages[0]))
        c.translate(w-6.125*inch, 0)
        c.doForm(makerl(c, pages1[0]))

        c.setFillColorRGB(0/256,0/256,102/256)
        c.setFont("SegoeUI", 10)
        text = "English - "+self.lang
        c.drawString((25/96)*inch, 8.2*inch, text)
        
        p = Paragraph(self.engTitle, self.styles['coverTitle'])
        p.wrapOn(c,(514/96)*inch, 3*inch)
        p.drawOn(c, (25/96)*inch, 4*inch)

        p = Paragraph(self.otherTitle, self.styles['coverTitle'])
        x,y=p.wrapOn(c,(514/96)*inch, 3*inch)
        p.drawOn(c, (25/96)*inch, 3.7*inch-y)

        p = Paragraph(self.coverSubTitle[0], self.styles['coverSubTitle'])
        p.wrapOn(c,5.3*inch, 1*inch)
        p.drawOn(c,(25/96)*inch, 0.7*inch)

        p = Paragraph(self.coverSubTitle[1], self.styles['coverSubTitle'])
        p.wrapOn(c,5.3*inch, 1*inch)
        p.drawOn(c, (25/96)*inch, 0.5*inch)
        
        c.save()
    

        
    def createPDF(self, found):
        doc = SimpleDocTemplate(self.path+"files\\"+self.docName+"English-"+self.lang+".pdf",showBoundary=0, pagesize=(6*inch,9*inch), leftMargin=0*inch, rightMargin=0*inch, topMargin=0.7*inch, bottomMargin=0.5*inch)
        j=0
        data1, message=self.getData(found)
        k=0
        if len(data1)==0:
            Text="""{} English - {} failed to be published because:{}""".format(self.docName,self.lang, message)
            self.sendEmail("ERROR",Text)
            return (False, message)
        self.engTitle=self.coverTitle[0]+" "+self.coverTitle[2]+" "+self.coverTitle[4]
        self.otherTitle=self.coverTitle[1]+" "+self.coverTitle[3]+" "+self.coverTitle[5]
        while j<3:
            try:
                elements = []
                t=Table((data1),colWidths=[2.5*inch]*2, style=[
                ('BOX',(0,0),(0,-1),1,colors.black),
                ('BOX',(0,0),(-1,-1),2,colors.white),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ])
                elements.append(t)
                doc.build(elements, onFirstPage=self.addPageNumber, onLaterPages=self.addPageNumber)
                
                j+=1
                if j==2:
                    with open(self.path+"files/"+self.docName+"English-"+self.lang+".pdf", "rb") as f:
                        pdf = PdfFileReader(f)
                        pages = pdf.pages
                        for index,page in enumerate(pages, start=1):
                            for index1,line in enumerate(page.extractText().splitlines(), start=0):
                                if len(line)<20 and len(line.split(" "))==2 and ((line.split(" ")[0]=="Article"and line.split(" ")[1].isdecimal()) or (line.split(" ")[0]=="ANNEX" and line.split(" ")[1].isalpha()) ):
                                    self.articleNum.append({"name":line, "pNum": index})
                                if line=="For the European Parliament":
                                    self.articleNum.append({"name":line, "pNum": index})
                
            except Exception as e:
                if k>10:
                    text = """{} English - {} failed to be published, because of the following error:\n
                    {}""".format(self.docName,self.lang, e)
                    self.sendEmail("ERROR",text)
                    j=2
                    return (False, str(e))
                else:
                    maxlength=479
                    data3=[]
                    engHeight=0
                    otherHeight=0
                    eng1=[]
                    other1=[]
                    
                    for item in data1:
                        text=item[0].text
                        if max(item[0].height, item[1].height)<(maxlength-engHeight):
                            letSplit=False
                            eng1.append(item[0])
                            other1.append(item[1])
                            engHeight+=max(item[0].height, item[1].height)
                        else:  
                            if (maxlength-engHeight)<26:
                                if max(item[0].height, item[1].height)>maxlength:
                                    if min(item[0].height, item[1].height)<maxlength:
                                        if item[0].height<maxlength:
                                            eng1.append(item[0])
                                            eng1.append(Paragraph("",self.styleA)) 
                                            otherItem=item[1].split(2.5*inch,item[0].height)
                                            other1.append(otherItem[0])
                                            other1.append(otherItem[1]) 
                                            engHeight=max(item[0].height, item[1].height)-item[0].height
                                        else:
                                            engItem=item[0].split(2.5*inch,item[1].height)
                                            eng1.append(engItem[0])
                                            eng1.append(engItem[1])
                                            other1.append(item[1])
                                            other1.append(Paragraph("",self.styleA))
                                            engHeight=max(item[0].height, item[1].height)-item[1].height
                                            
                                    else:
                                        engItem=item[0].split(2.5*inch,maxlength)
                                        eng1.append(engItem[0])
                                        eng1.append(engItem[1])
                                        otherItem=item[1].split(2.5*inch,maxlength)
                                        other1.append(otherItem[0])
                                        other1.append(otherItem[1]) 
                                        engHeight=max(item[0].height, item[1].height)-maxlength
                                    
                                elif min(item[0].height, item[1].height)<26:
                                    if item[0].height>25:   
                                        engItem=item[0].split(2.5*inch,25)
                                        eng1.append(engItem[0])
                                        eng1.append(engItem[1])
                                    else:
                                        eng1.append(item[0])
                                        eng1.append(Paragraph("",self.styleA)) 
                                    if item[1].height>25:
                                        otherItem=item[1].split(2.5*inch,25)
                                        other1.append(otherItem[0])
                                        other1.append(otherItem[1])     
                                    else:
                                        other1.append(item[1])
                                        other1.append(Paragraph("",self.styleA))     
                                    engHeight=max(item[0].height, item[1].height)-25
                                else:
                                    eng1.append(item[0])
                                    other1.append(item[1])
                                    engHeight=max(item[0].height, item[1].height)
                            else:
                                if (maxlength-engHeight)>=item[0].height:
                                    eng1.append(item[0])
                                    eng1.append(Paragraph("",self.styleA))
                                else:
                                    engItem=item[0].split(2.5*inch,maxlength-engHeight)
                                    eng1.append(engItem[0])
                                    eng1.append(engItem[1])
                                if (maxlength-engHeight)>=item[1].height:
                                    other1.append(item[1])
                                    other1.append(Paragraph("",self.styleA))
                                else:
                                    otherItem=item[1].split(2.5*inch,maxlength-engHeight)
                                    other1.append(otherItem[0])
                                    other1.append(otherItem[1])
                                engHeight=max(item[0].height, item[1].height)-(maxlength-engHeight)
                        
                    for i in range(0,len(eng1)):
                        row1=[]
                        row1.append(eng1[i])
                        row1.append(other1[i])
                        data3.append(row1)
                    data1=data3
                    k+=1
                    j=1


                    
        if self.pageNum<25:
            os.remove(self.path+"files/"+self.docName+"English-"+self.lang+".pdf")
            Text="""{}, English - {} failed to be published because: Less then 24 pages""".format(self.docName, self.lang)
            self.sendEmail("ERROR",Text)
            return (False, "Less then 24 pages")
        
        else:
            self.createFirstPage()
            if (self.pageNum+2)%4!=0:
                M=PdfFileMerger()
                M.append(self.path+"files\\"+self.docName+"English-"+self.lang+".pdf")
                M.write(self.path+"convert.pdf")
                M.close()
                M=PdfFileMerger()
                M.append(self.path+"convert.pdf")
                M.append(self.path+"frames\\"+"blank"+str(4-(self.pageNum+2)%4)+".pdf")
                M.write(self.path+"files\\"+self.docName+"English-"+self.lang+".pdf")
                M.close()
                os.remove(self.path+"convert.pdf")
                
            self.addCover()
            return (True, "")


# In[6]:


books=lawScrapper()
books.Start()


# In[ ]:




