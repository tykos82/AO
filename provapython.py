import sys
sys.path.insert(0, 'lib')
import urllib
import re
#import HTMLParser

from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#--BEGIN----FUNZIONI PER AGGIORNARE GOOGLE SHEETS-----------------------------------
def numberToLetters(q):
    """
    Helper function to convert number of column to its index, like 10 -> 'A'
    """
    q = q - 1
    result = ''
    while q >= 0:
        remain = q % 26
        result = chr(remain+65) + result;
        q = q//26 - 1
    return result

def colrow_to_A1(col, row):
    return numberToLetters(col)+str(row)

def update_sheet(ws, rows, left=1, top=1):
    """
    updates the google spreadsheet with given table
    - ws is gspread.models.Worksheet object
    - rows is a table (list of lists)
    - left is the number of the first column in the target document (beginning with 1)
    - top is the number of first row in the target document (beginning with 1)
    """

    # number of rows and columns
    num_lines, num_columns = len(rows), len(rows[0])

    # selection of the range that will be updated
    cell_list = ws.range(
        colrow_to_A1(left,top)+':'+colrow_to_A1(left+num_columns-1, top+num_lines-1)
    )

    # modifying the values in the range

    for cell in cell_list:
        val = rows[cell.row-top][cell.col-left]
        cell.value = val

    # update in batch
    ws.update_cells(cell_list)
 #--END----FUNZIONI PER AGGIORNARE GOOGLE SHEETS-----------------------------------
 

def estrai_numerogiornata(titolo):
    """
    Cerca nella stringa titolo il numero della giornata e lo converte in formato 0000
    """
    regex = ur"(?<=day )[0-9]*"
    numero_puro = re.search(regex, titolo, re.UNICODE)
   # print numero_puro.group(0)
    
    #numero_quattrocifre = '%04d' % numero_puro.group(0)
    numero_quattrocifre = numero_puro.group(0).zfill(4)
    
    #print numero_quattrocifre
    return numero_quattrocifre


def prova():
  test_str = "14 maggio 2002, day 12, 23:50 GMT+5: Treno n10 Baikal Express da Mosca a Irkutsk, linea Transiberiana - Day 2"
  regex = ur"day [0-9]*"
  matches = re.findall(regex, test_str)
  print matches[0]
 
 
def provapython():
#--BEGIN PRENDI VALORI DA GOOGLE SHEETS
  json_key = 'gspread-test.json'
  scope = ['https://spreadsheets.google.com/feeds']

  credentials = ServiceAccountCredentials.from_json_keyfile_name('gspread-test.json', scope)
  gc = gspread.authorize(credentials)
  wks_tappe = gc.open("AO20").sheet1
  wks_bonus = gc.open("AO20").worksheet("Sheet2")
  elenco_link_gsheet = wks_tappe.col_values(2) # crea lista_tappe con campo link
  elenco_bonus_gsheet = wks_bonus.col_values(2) # crea lista_bonus con campo link
 #print elenco_bonus_gsheet

  #--END PRENDI VALORI DA GOOGLE SHEETS

  list_of_lists_tappe = wks_tappe.get_all_values() # crea lista di liste
  list_of_lists_bonus = wks_bonus.get_all_values() # crea lista di liste

  #print list_of_lists

  #### update_sheet(wks, list_of_lists) # aggiornamento riordinato del foglio google sheets
        
  url = 'https://www.frenf.it/earlyadopters/rss/AsiaOverland2002'
  res = urllib.urlopen(url)
  html = res.read()

  soup = BeautifulSoup(html, 'xml')

  giornata = soup.findAll('item')

  for ognigiornata in giornata:
    if ognigiornata.creator.string == 'orizzontintorno':
      titolo = ognigiornata.title.string
      #print titolo
      link = 'https://www.frenf.it' + ognigiornata.link.string
      #print link
      timestamp = ognigiornata.date.string
      #print timestamp
      #numero_quattrocifre = estrai_numerogiornata(titolo)
      if ((ognigiornata.title.string[:1].isdigit())):
        numero_quattrocifre = estrai_numerogiornata(titolo)
        #print "AA" + numero_quattrocifre
        if (link not in elenco_link_gsheet):
          wks_tappe.append_row([titolo, link, numero_quattrocifre, timestamp])
          #list_of_lists_tappe.sort(key = lambda row: row[2]) #ordina lista di liste
      else: #(link not in elenco_bonus_gsheet):
        print "OK"
        if (link not in elenco_bonus_gsheet): wks_bonus.append_row([titolo, link, timestamp])
        
      list_of_lists_tappe.sort(key = lambda row: row[2]) #ordina lista di liste
      list_of_lists_bonus.sort(key = lambda row: row[2]) #ordina lista di liste bonus
      
  return list_of_lists_tappe, list_of_lists_bonus
  
      
    #print "numero finale" + numero_quattrocifre
    
   # if link in elenco_link_gsheet:
   #   print ('')
   # else:
   #   elenco_link_gsheet.extend(link)
   #   print 'AGGIUNTO' + link
   # if ((link not in elenco_link_gsheet) and (ognigiornata.title.string[:1].isdigit())):
   #   wks.append_row(titolo, link, timestamp)