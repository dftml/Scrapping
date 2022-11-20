from shiny import App, render, ui, reactive
import requests                                                           # to open and read  the url
from urllib.request import urlopen                                        # to open and read  the url
from bs4 import BeautifulSoup                                             # to navigate and search the url
import csv                                                                # to export the data
import pandas as pd                                                       # for extract table from html page and create DataFrame
import pymongo
from pathlib import Path


app_ui = ui.page_fluid( ui.tags.style(
        """
        .app-col {
            border: 1px solid black;
            border-radius: 5px;
            background-color: 	#afeeee;
            padding: 12px;
            margin-top: 1px;
            margin-bottom: 5px;
        }
        """
    """.apps-col {
            border: 1px solid black;
            border-radius: 5px;
            background-color: #90ee90;
            padding: 12px;
            margin-top: 1px;
            margin-bottom: 5px;
        }
        """
    ),
    ui.h6({"style": "text-align: right;"}, "Hemant Kumar"),
    ui.h1({"style": "text-align: center;"}, "Flipkart Search Engine"),
    ui.row(
        ui.column(8,ui.panel_well(
                    ui.input_text("x1","Search Product" ),
                    ui.input_action_button("btn","Search"))),
        ui.column(4,ui.div({"class": "app-col"},
                ui.p(ui.input_radio_buttons("x2","Mode of Navigations", choices={"S":"Single Page", "R" : "Multi Page"}),
                    ui.output_ui("Page"))))),
    ui.row(
        ui.column(8,
                ui.div({"class": "apps-col"},
                ui.p(("""There is a restriction of 10 pages for navigation and data scraping on Flipkart. """)),
                    ui.p("""Search and hold out for a while. It takes a few minutes.""")
                             ))),
                       

    ui.row(
        ui.column(12,ui.div({"class": "appss-col"},
                ui.p(
                    ui.download_button("download1","Download Table"))))),
    ui.row(
        ui.column(12,ui.div({"class": "appss-col"},
                ui.p(
                    ui.output_table("Table")))))
)

def server(input, output, session):
    @output
    @render.ui()
    def Page():
        if input.x2() == "S":
            return ui.page_fluid(ui.input_numeric("x3","Specific Page", min=1, step=1, value=1))
        
        if input.x2() == "R":
            return ui.page_fluid(ui.input_numeric("x4","Starting Page Index", min=1, step=1, value=1),
                                 ui.input_numeric("x5","Ending Page Index", min=1, step=1, value=3))

    def table_generator():
        # Mention the service provider and search decorator of url
        service_url = "https://www.flipkart.com"
        search_url = "https://www.flipkart.com/search?q="

        # input("Please enter the product : ")
        search = input.x1()
        
        parent_service_url = search_url + search
        
        try:
            read1 = requests.get(parent_service_url)
            parse_tree1 = BeautifulSoup(read1.text,
                                        "html.parser")                            # html.parser library helps to convert data into structured format or nested form
            navigator_1 = parse_tree1.find("nav", {"class": "yFHi8N"})            # search number of navigation page on parent html
            items_list_navigator = navigator_1.find_all("a", {"class": "ge-49M"}) # find all the navigator container
            items_url = []
            for item in items_list_navigator:
                items_url.append(item['href'])                                    # collect all the links of navigation page container
        
        # Exception for only first page
        except:
            item = "/search?q=" + search                                          # if no navigator page found it create direct parent html link
            items_url = []
            items_url.insert(0, item)                                             # collect direct parent html link
        
        
        else:
            # input(f"Please input mode of navigation from {len(items_url)} html page\n
            # Press S for single page\nPress R for range of pages\nEnter S or R : ")
            navigator_2 = input.x2()
        
            if navigator_2 == "S":
                # input(f"Please input any single page you want to navigate from {len(items_url)} html page : ")
                page = input.x3()
                item = items_url[int(page) - 1]                                 # from list find single index it gives primitive data type
                items_url = []
                items_url.insert(0, item)                                       # select use html page & again insert in list
        
            elif navigator_2 == "R":
                print(f"Please input how many page you want to navigate total {len(items_url)} pages on search html : ")
                # input("Value of Start Page : ")
                page_start = input.x4()
                # input("Value of Final Page : ")
                page_final = input.x5()
                items_url = items_url[
                            int(page_start) - 1:int(page_final)]               # select only user defined range of html page for navigation
        
            if len(items_url) == 1:
                if items_url[0][-6:-1] + items_url[0][-1] == "page=1":
                    item = "/search?q=" + search                               # for 1st page navigation it creates direct parent html link
                    items_url = []
                    items_url.insert(0, item)                                  # collect direct parent html link
        
        list_data = []
        for content_url in items_url:
            item_service_url = service_url + content_url
            read2 = requests.get(item_service_url)
            parse_tree2 = BeautifulSoup(read2.text, "html.parser")
            items_list = parse_tree2.find_all("a", {"class": "_1fQZEK"})
        
            # if all the items not arrange in columns then it does not find anything
            if len(items_list) == 0:  # empty list shows
                items_list = parse_tree2.find_all("a", {"class": "s1Q9rs"})  # it means that all items arrange in row form
        
            for item_index in range(len(items_list)):
                child_service_url = service_url + items_list[item_index]['href']
                html_1 = urlopen(child_service_url)
                read3 = html_1.read()
                html_1.close()
                parse_tree3 = BeautifulSoup(read3, "html.parser")
        
                try:
                    table_all = pd.read_html(child_service_url)
                    dict_1 = {}
                    for table in range(len(table_all)):
                        create_df = pd.DataFrame(table_all[table])  # for each table DataFrame is created
        
                        for row_index in range(len(create_df)):
                            dict_1[create_df[0][row_index]] = create_df[1][row_index]
        
                except:
                    pass
        
                try:
                    rating = parse_tree3.find("div", {"class": "_3LWZlK"}).text
                except:
                    rating = "Not Mention"
        
                try:
                    price = parse_tree3.find("div", {"class": "_30jeq3 _16Jk6d"}).text
                except:
                    price = "Not Mention"
        
                try:
                    model = parse_tree3.find("span", {"class": "B_NuCI"}).text
                except:
                    model = "Not Mention"
        
                try:
                    people_rating = parse_tree3.find("span", {"class": "_2_R_DZ"})
                    total_no_rate = people_rating.span.span.text[:-1]
                except:
                    total_no_rate = "Not Mention"
        
                try:
                    people_review = parse_tree3.find("div", {"class": "_3UAT2v _16PBlm"})
                    total_no_review = people_review.span.text[4:]  # All review section taking reviews
                except:
                    total_no_review = "Not Mention"
        
                dict_2 = {"Model": model, "Price": price, "Rating": rating, "Total Rating": total_no_rate,
                          "Total Reviews": total_no_review}
                
                dict_2.update(dict_1)
        
                list_data.append(dict_2)
        
        return list_data
    
    @output
    @render.table()
    @reactive.event(input.btn)
    def Table():
        client = pymongo.MongoClient("mongodb+srv://dftML:dftML@stano.mez9zwp.mongodb.net/?retryWrites=true&w=majority")
        database = client["Search_Engine"]
        collection = database["Data_Search"]
        collection.drop()
        collection.insert_many(table_generator())
        return pd.DataFrame(list(collection.find())).iloc[:,1:]

    @session.download(filename=f"data.csv")
    def download1():
        client = pymongo.MongoClient("mongodb+srv://dftML:dftML@stano.mez9zwp.mongodb.net/?retryWrites=true&w=majority")
        database = client["Search_Engine"]
        collection = database["Data_Search"]
        df1 = pd.DataFrame(list(collection.find())).iloc[:,1:]

        download_path = str(Path.home() / "Downloads")
        
        if download_path[0] == "C":
            return df1.to_csv(f"{download_path}\\{input.x1()}.csv")
        
        return df1.to_csv(f"{download_path}/{input.x1()}.csv")



app = App(app_ui, server)
