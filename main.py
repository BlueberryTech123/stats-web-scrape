import requests
from bs4 import BeautifulSoup
import os
import pandas
import csv
import io

url_afford = "https://lao.ca.gov/LAOEconTax/Article/Detail/793" # june 2024
response_afford = requests.get(url_afford)
html_parse_afford = BeautifulSoup(response_afford.text, "html.parser")

url_cpop = "https://www2.census.gov/programs-surveys/popest/tables/2020-2023/counties/totals/co-est2023-pop-06.xlsx" # july 2023
response_cpop = requests.get(url_cpop)
# html_parse_cpop = BeautifulSoup(response_cpop.text, "html.parser")
excel_file = io.BytesIO(response_cpop.content)
xlsx_parse = pandas.read_excel(excel_file)

url_csize = "https://web.archive.org/web/20080605065216/http://www.naco.org/Template.cfm?Section=Find_a_County&Template=%2Fcffiles%2Fcounties%2Fstate.cfm&state.cfm&statecode=CA"
response_csize = requests.get(url_csize)
html_parse_csize = BeautifulSoup(response_csize.text, "html.parser")

table_content_csize = html_parse_csize.find_all("tr")

data = {}
returned_csv = [
    ["name", "size", "population", "rent", "house", "density"]
]
def findIndexByCounty(county):
    for i in range(len(returned_csv)):
        returned_csv[i][0] == county
        return i
    return 0

# county sizes
for i in table_content_csize:
    row_items = i.find_all("td")
    county = None
    if len(row_items) != 6: continue
    if len(row_items[0].find_all("a")) == 1:
        county = row_items[0].text.lower().replace("\n", "")
    else: continue

    if "county" not in county: continue
    if "california" in county: continue
    if "san francisco county" in county: county = "san francisco county"

    da_size = row_items[3].text.replace("\n", "").replace(" ", "").replace(",", "").replace("\t", "")
    da_size = float(str(da_size)) # in sq mi

    # print(f"COUNTY: {county}; SIZE: {da_size} sq mi")
    data[county] = { "size": da_size, "population": -1, "rent": -1, "house": -1, "density": -1 }

# population and density
index = 0
for row in xlsx_parse.itertuples(index=False):
    if not (index > 3 and index < 62):
        index += 1
        continue
    
    county = row._0.replace(", California", "").replace(".", "").lower()
    population = row._5
    # write
    # print(f"COUNTY: {county}; POP: {population} people")
    data[county]["population"] = population
    data[county]["density"] = 1.0 * data[county]["population"] / data[county]["size"]
    # print(data[county]["density"])
    index += 1

# rent
index = 0
csv_parse = pandas.read_csv("housing.csv")
for row in csv_parse.itertuples(index=False):
    if index == 0:
        index += 1
        continue
    
    county = row.regionname.lower() + " county"
    # print(county)
    rent = row.Rents
    house = row._1
    # # write
    # # print(f"COUNTY: {county}; POP: {population} people")
    data[county]["rent"] = rent
    data[county]["house"] = house
    # # print(data[county]["density"])
    index += 1

# map data
for key in data:
    returned_csv.append([
        key, # name
        data[key]["size"],
        data[key]["population"],
        data[key]["rent"],
        data[key]["house"],
        data[key]["density"]
    ])

with open("data.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    
    # Write each row of data to the CSV file
    writer.writerows(returned_csv)