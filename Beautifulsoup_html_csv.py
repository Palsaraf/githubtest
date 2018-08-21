from BeautifulSoup import BeautifulSoup
import csv
import requests

outputfile = "allthedata.csv"
csvfile = open(outputfile, 'wb')
fout = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

baseUrl = "http://omms.nic.in/StateProfile/StateProfile/HabitationPopulationStatus/"
tablecount = -1

for year_base in range(17):
  for statecode_base in range(36):
    for populationCode in [1, 2, 4, 5]:
      for upgradeStatus in ["N", "U"]:
        year = year_base + 2000
        statecode = statecode_base + 1
        url = baseUrl + str(populationCode) + "$" + str(statecode) + "$0$0$2$" + str(year) + "$0$" + upgradeStatus + "$R$0$Y$0$0"

        print "curling " + str(populationCode) + " " + str(statecode) + " " + str(year) + " " + upgradeStatus
        htmltext = requests.get(url).text

        print "Parsing htmltext"
        soup = BeautifulSoup(htmltext,convertEntities=BeautifulSoup.HTML_ENTITIES)

        print "Preemptively removing unnecessary tags"
        [s.extract() for s in soup('script')]

        print "writing to CSV"
        for table in soup.findAll("table"):
          tablecount += 1
          print "Processing Table #%d" % (tablecount)
          for row in table.findAll('tr'):
            cols = row.findAll(['td'])
            if cols:
              cols = [x.text for x in cols]
              cols.append(year)
              cols.append(statecode)
              cols.append(populationCode)
              cols.append(upgradeStatus)
              fout.writerow(cols)