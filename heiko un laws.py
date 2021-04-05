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
from PyPDF2 import PdfFileMerger


# In[5]:


class lawScrapper:
    pageNum=0
    path="/Users/shantjoulfayan/Documents/heiko/"
    url=""
    lang=""
    coverTitle=[]
    coverSubTitle=[]
    articleNum=[]
    docName=""
    resultsNum=0
    topTitle="Recitals"
    currentBookNum=1
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
    excelNum=1
    styles.add (ParagraphStyle('coverSubTitle',
                               fontName="SegoeUI",
                               textColor="#000066",
                               fontSize=9, alignment=TA_JUSTIFY))
    styles.add (ParagraphStyle('coverTitle',
                               fontName="SegoeUI",
                               textColor="#000066",
                               fontSize=10, alignment=TA_JUSTIFY))
    
    
    def __init__(self):
        pdfmetrics.registerFont(TTFont('SegoeUI', '/Users/shantjoulfayan/Documents/heiko/segoe-ui/SEGOEUI.TTF'))
        
    def Start(self):          
        driver = webdriver.Chrome("/Users/shantjoulfayan/Downloads/chromedriver")
        driver.get("https://eur-lex.europa.eu/homepage.html")
        a=driver.find_element_by_xpath("//a[text()='Legal acts']")
        driver.execute_script("arguments[0].click();", a)
        a=driver.find_element_by_xpath("//a[text()='Search in legal acts']")
        driver.execute_script("arguments[0].click();", a)
        driver.find_element_by_xpath("//input[@id='legInForce']").click()
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
        for i in range(1,self.resultsNum+1):
            self.currentBookNum=i
            try:
                if i%100==1:
                    workbook = xlsxwriter.Workbook(self.path+str(self.excelNum)+'.xlsx')
                    worksheet = workbook.add_worksheet()
                    columnNames=['Interior File Path','Cover File Path','Title','Subtitle','Author - Prefix','Author - First Name','Author - Middle Name','Author - Last Name','Author - Suffix', 'Description','Keyword #1','Keyword #2','Keyword #3','Keyword #4','Keyword #5','Keyword #6','Keyword #7','Price','Category #1','Category #2','Primary Marketplace','Expanded Distribution', 'Round Price To#.99 After VAT' ]
                    row=0
                    for item in columnNames:
                        worksheet.write(0,row,item)
                        row+=1

                select = Select(driver.find_element_by_id('MDLang2'))
                for j in range(0,len(select.options)):
                    select = Select(driver.find_element_by_id('MDLang2'))
                    select.select_by_index(j)
                    selected_option = select.first_selected_option
                    self.lang=selected_option.text.split(" ")[0]
                    self.articleNum=[]
                    self.coverTitle=[]
                    self.coverSubTitle=[]
                    self.topTitle="Recitals"
                    if self.lang!="English":
                        a=driver.find_element_by_xpath("//button[text()='Display']")
                        driver.execute_script("arguments[0].click();", a)
                        result=self.getStarted(driver)
                a=driver.find_element_by_xpath("//span[text()='Next']")
                driver.execute_script("arguments[0].click();", a)

                if result==True:
                    self.addRowtoExcel(worksheet)
                    if i%100==0:
                        workbook.close()
                        self.sendEmail("Success","Excel number {} is ready to be uploaded.".format(self.excelNum))
                        self.excelNum+=1
            except Exception as e:
                print(e)
                break
            if i==3:
                break
                
#         self.sendEmail("Success","Done downloading the books.")
            
    
    def getStarted(self, driver):
        page_soup = BeautifulSoup(driver.page_source, "html.parser")
        self.docName=page_soup.findAll('h1',{"class":"DocumentTitle"})[0].getText()
        found= page_soup.findAll("table",{"class":"table-responsive"})
        result=self.createPDF(found)
    
    def addRowtoExcel(self, worksheet):
        Description="""We have 24 official languages in the European Union. English remains an official EU language even after Brexit.
European legislation is subject to interpretation. Due to the variety of language versions, there are a number of linguistic differences. The book series "European Union Law - The Bilingual Editions" intends to allow multiple linguistic versions to be used for interpretation.
Therefore, in our book series, the English legal texts are published in addition to a second language version to enable simple comparison of European legal provisions and make interpretation easier."""
        worksheet.write(((self.currentBookNum-1)%100+1),0,"files/"+self.docName+"English-"+self.lang+".pdf" )
        worksheet.write(((self.currentBookNum-1)%100+1),1,"covers/"+self.docName+"English-"+self.lang+".pdf" )
        worksheet.write(((self.currentBookNum-1)%100+1),2,self.coverTitle[0] )
        worksheet.write(((self.currentBookNum-1)%100+1),3,coverTitle[1] )
        worksheet.write(((self.currentBookNum-1)%100+1),5,"Heiko" )
        worksheet.write(((self.currentBookNum-1)%100+1),6,"Jonny" )
        worksheet.write(((self.currentBookNum-1)%100+1),7,"Maniero" )
        worksheet.write(((self.currentBookNum-1)%100+1),8,Description )
        worksheet.write(((self.currentBookNum-1)%100+1),9,self.coverTitle[0] )
        worksheet.write(((self.currentBookNum-1)%100+1),10,self.coverTitle[1] )
        worksheet.write(((self.currentBookNum-1)%100+1),11,self.coverSubTitle[0])
        worksheet.write(((self.currentBookNum-1)%100+1),12,self.coverSubTitle[1] )
        worksheet.write(((self.currentBookNum-1)%100+1),13,"European law" )
        worksheet.write(((self.currentBookNum-1)%100+1),14,"EU law" )
        worksheet.write(((self.currentBookNum-1)%100+1),15,"EU Regulation" )
        worksheet.write(((self.currentBookNum-1)%100+1),16,7.99 )
        worksheet.write(((self.currentBookNum-1)%100+1),17,"Nonfiction > Law > Civil Law" )
        worksheet.write(((self.currentBookNum-1)%100+1),18,"Nonfiction > Law > International" )
        worksheet.write(((self.currentBookNum-1)%100+1),17,"Amazon.de" )
        worksheet.write(((self.currentBookNum-1)%100+1),17,"YES" )
        worksheet.write(((self.currentBookNum-1)%100+1),17,"YES" )
        
    def sendEmail(self, subject,  text):
        message = MIMEMultipart("alternative")
        message["From"] = "ChantHeiko@gmail.com"
        message["To"] = "joulfaian8@gmail.com"
        message["Subject"] = subject
        message.Subject = subject
        part1 = MIMEText(text, "plain")
        message.attach(part1)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, self.receiver_email, message.as_string())
            
            
    def getData(self, found):
        data=[]
        j=1
        if found is None or len(found)==0:
            return ([], "no html table body")
        for line in found[0].findAll('tr'):
            row=[]
            i=1
            P0=[]
            for l in line.findAll('td'):
                if j==2:
                    if len(l.getText())>968:
                        return ([], "Title too long")
                    self.coverTitle.append(l.getText()) 
                elif j==1:
                    if len(l.getText())>76:
                        return ([], "SubTitle too long")
                    self.coverSubTitle.append(l.getText())         
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
        canvas.setLineWidth(3)
        text2=""
        topTitle2=""
        for item in self.articleNum:
            if item["pNum"]==self.pageNum:
                if item["name"]=="For the European Parliament":
                    topTitle=""
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
        if self.pageNum>=3:
            canvas.drawRightString(5.5*inch, 0.3*inch, text)
        canvas.line(0.5*inch, 0.5*inch,5.5*inch, 0.5*inch)
        self.topTitle=topTitle2 or topTitle
        
    def createFirstPage(self):
        c  = canvas.Canvas('/Users/shantjoulfayan/Documents/heiko/firstPage.pdf', pagesize=(6*inch, 9*inch))
        I = Image('/Users/shantjoulfayan/Downloads/Frame111.jpg')
        I.drawHeight = (502/96)*inch
        I.drawWidth = (453/96)*inch
        I.drawOn(c, ((6-(453/96))/2)*inch, (8.7-(502/96))*inch)

        I = Image('/Users/shantjoulfayan/Downloads/Frame112.jpg')
        I.drawHeight = (75/96)*inch
        I.drawWidth = (453/96)*inch
        I.drawOn(c,  ((6-(453/96))/2)*inch, 0.3*inch)

        c.setFillColorRGB(0/256,0/256,6/256)
        c.setFont("SegoeUI", 14)
        text = "English - "+self.lang+" - First Edition"
        c.drawCentredString(3*inch, 8*inch, text)

        p = Paragraph(self.coverTitle[0], self.styles['coverTitle'])
        p.wrapOn(c,4.7*inch, 3*inch)
        p.drawOn(c, ((6-(453/96))/2)*inch, 3.6*inch)

        p = Paragraph(self.coverTitle[1], self.styles['coverTitle'])
        x,y=p.wrapOn(c,4.7*inch, 3*inch)
        p.drawOn(c,((6-(453/96))/2)*inch, 3.4*inch-y)
        c.save()
        M=PdfFileMerger()
        M.append(self.path+"firstPage.pdf")
        M.append(self.path+"Frame44.pdf")
        M.write(self.path+"First2Pages.pdf")
        M.close()
        M=PdfFileMerger()
        M.append(self.path+"files/"+self.docName+"English-"+self.lang+".pdf")
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
        w=12*inch+((self.pageNum+2)+(self.pageNum+2)%4)* 0.002252*inch
        c  = canvas.Canvas(self.path+'covers/'+self.docName+"English-"+self.lang+'.pdf', pagesize=(w, 9*inch))
        c.setFillColorRGB(228/256,240/256,255/256)
        c.rect(0*mm,7.5*inch,w,9*inch,stroke=0, fill=1)    
        c.setFillColorRGB(5/256,92/256,157/256)
        c.rect(0*mm,1.225*inch,w,6.275*inch,stroke=0, fill=1)    
        c.setFillColorRGB(228/256,240/256,255/256)
        c.rect(0*mm,0*inch,w,1.225*inch,stroke=0, fill=1)
        
        if self.currentBookNum%400<101:
            I = Image('/Users/shantjoulfayan/Downloads/Frame7.jpg')
        elif self.currentBookNum%400<201:
            I = Image('/Users/shantjoulfayan/Downloads/Frame77.jpg')
        elif self.currentBookNum%400<301:
            I = Image('/Users/shantjoulfayan/Downloads/Frame88.jpg')
        else:
            I = Image('/Users/shantjoulfayan/Downloads/Frame66.jpg')
        I.drawHeight = 9*inch
        I.drawWidth = 6*inch
        I.drawOn(c, 0, 0)

        I = Image('/Users/shantjoulfayan/Downloads/frame10.jpg')
        I.drawHeight = 6.275*inch
        I.drawWidth =  6*inch
        I.drawOn(c, 6*inch+60* 0.002252*inch, 1.225*inch)


        I = Image('/Users/shantjoulfayan/Downloads/frame49.jpg')
        I.drawHeight = 1.225*inch
        I.drawWidth =  6*inch
        I.drawOn(c, 6*inch+60* 0.002252*inch,0*inch)

        I = Image('/Users/shantjoulfayan/Downloads/Frame29.jpg')
        I.drawHeight = 1.5*inch
        I.drawWidth =  6*inch
        I.drawOn(c, 6*inch+60* 0.002252*inch,7.5*inch)

        c.setFillColorRGB(0/256,0/256,102/256)
        c.setFont("SegoeUI", 10)
        text = "English - "+self.lang
        c.drawString(w-5.75*inch, 7.9*inch, text)

        p = Paragraph(self.coverTitle[0], self.styles['coverTitle'])
        p.wrapOn(c,5.3*inch, 3*inch)
        p.drawOn(c, w-5.75*inch, 3.9*inch)

        p = Paragraph(self.coverTitle[1], self.styles['coverTitle'])
        x,y=p.wrapOn(c,5.3*inch, 3*inch)
        p.drawOn(c, w-5.75*inch, 3.6*inch-y)

        p = Paragraph(self.coverSubTitle[0], self.styles['coverSubTitle'])
        p.wrapOn(c,5.3*inch, 1*inch)
        p.drawOn(c, w-5.75*inch, 0.7*inch)

        p = Paragraph(self.coverSubTitle[1], self.styles['coverSubTitle'])
        p.wrapOn(c,5.3*inch, 1*inch)
        p.drawOn(c, w-5.75*inch, 0.5*inch)
        
        c.save()
    
    def fixLayout(self, data):
        maxlength=502
        self.articleNum=[]
        pageNum=1
        data3=[]
        engHeight=0
        otherHeight=0
        eng1=[]
        other1=[]
        for item in data:
            text=item[0].text
            if engHeight+max(item[0].height, item[1].height)<maxlength:
                eng1.append(item[0])
                other1.append(item[1])
                engHeight+=max(item[0].height, item[1].height)
            else:
                pageNum+=1
                if (maxlength-engHeight)<26:
                    if min(item[0].height, item[1].height)<21:
                        if item[0].height>24:                       
                            engItem=item[0].split(2.5*inch,25)
                            eng1.append(engItem[0])
                            eng1.append(engItem[1])
                        else:
                            eng1.append(item[0])
                            eng1.append(Paragraph("",self.styleA)) 
                        if item[1].height>24:
                            otherItem=item[1].split(2.5*inch,25)
                            other1.append(otherItem[0])
                            other1.append(otherItem[1])     
                        else:
                            other1.append(item[1])
                            other1.append(Paragraph("",self.styleA))     
                        engHeight=max(item[0].height, item[1].height)-24
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
            if not text is None:
                if len(text)<20 and len(text.replace(u'\xa0', u' ').split(" "))==2 and text.replace(u'\xa0', u' ').split(" ")[0]=="Article" or text.replace(u'\xa0', u' ').split(" ")[0]=="ANNEX":
                    self.articleNum.append({"name":text.replace(u'\xa0', u' '), "pNum":pageNum})
                if text.replace(u'\xa0', u' ')=="For the European Parliament":
                    self.articleNum.append({"name":text.replace(u'\xa0', u' '), "pNum":pageNum})
        for i in range(0,len(eng1)):
            row1=[]
            row1.append(eng1[i])
            row1.append(other1[i])
            data3.append(row1)
        return (data3)
        
    def createPDF(self, found):
        doc = SimpleDocTemplate(self.path+"files/"+self.docName+"English-"+self.lang+".pdf",showBoundary=0, pagesize=(6*inch,9*inch), leftMargin=0*inch, rightMargin=0*inch, topMargin=0.7*inch, bottomMargin=0.5*inch)
        j=0
        data1, message=self.getData(found)
        k=0
        if len(data1)==0:
            Text="""{} failed to be published because:{}""".format(self.docName, message)
            self.sendEmail("ERROR",Text)
            return False
        while j<2:
            try:
                elements = []
                if j==1:
                    data1=self.fixLayout(data1)
                t=Table((data1),colWidths=[2.5*inch]*2, style=[
                ('BOX',(0,0),(0,-1),1,colors.black),
                ('BOX',(0,0),(-1,-1),2,colors.white),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ("-pdf-keep-in-frame-mode",(0,0),(-1,-1), "shrink")
                ])
                elements.append(t)
                doc.build(elements, onFirstPage=self.addPageNumber, onLaterPages=self.addPageNumber)
                
                j+=1
                self.addCover()
            except Exception as e:
                if k>10:
                    text = """{} failed to be published, because of the following error:\n
                    {}""".format(self.docName, e)
                    self.sendEmail("ERROR",text)
                    j=2
                    return False
                else:
                    k+=1
                    j=1

                    
        if self.pageNum<25:
            os.remove(self.path+"files/"+self.docName+"English-"+self.lang+".pdf")
            Text="""{} failed to be published because: Less then 24 pages""".format(self.docName)
            self.sendEmail("ERROR",Text)
            return False
        
        self.createFirstPage()
        if (self.pageNum+2)%4!=0:
            M=PdfFileMerger()
            M.append(self.path+"files/"+self.docName+"English-"+self.lang+".pdf")
            M.write(self.path+"convert.pdf")
            M.close()
            M=PdfFileMerger()
            M.append(self.path+"convert.pdf")
            M.append(self.path+"blank"+str((self.pageNum+2)%4)+".pdf")
            M.write(self.path+"files/"+self.docName+"English-"+self.lang+".pdf")
            M.close()
            os.remove(self.path+"convert.pdf")
        self.addCover()
        return True


# In[6]:


books=lawScrapper()
books.Start()


# In[ ]:




