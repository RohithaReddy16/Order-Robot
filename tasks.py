from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():

    open_robot_order_website()
    close_annoying_popup()
    download_csv_file()

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    
def download_csv_file():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    
    columns = read_csv_file() 
    for row in columns:
        submit_robot(row)
        click_another_order()
        close_annoying_popup()
    archive_receipts()
def read_csv_file():
    library = Tables()
    return library.read_table_from_csv(
    "orders.csv", columns=["Order number", "Head", "Body","Legs","Address"]
)
    
def close_annoying_popup():
    page = browser.page()
    page.click("button:text('OK')")
    
def submit_robot(row):
    page = browser.page()
    page.select_option('//div/select[@id="head"][@class="custom-select"]',row["Head"])
    body = row["Body"]
    page.check("#id-body-{}".format(body))
    page.fill('//div/input[@class="form-control"][@max="6"]', row["Legs"])
    page.fill('//div/input[@class="form-control"][@name="address"]', row["Address"])
    page.click('//form/button[contains(text(),"Order")]')
    check_err_block()
    receipt_no = page.locator('//div/div/p[@class="badge badge-success"]').inner_text()
    download_pdf(receipt_no)
    screen_shot_robot(receipt_no)

def download_pdf(receipt_no):
    page = browser.page()
    inner_html = page.locator('//div/div[@id="order-completion"]').inner_html()
    pdf = PDF()
    pdf.html_to_pdf(inner_html, "output/receipts/{}.pdf".format(receipt_no))
    # page.locator('#robot-preview-image').screenshot(path="output/sales_summary.png")
    
    
def screen_shot_robot(receipt_no):
    page = browser.page()
    # inner_html = page.locator('//div/div[@id="order-completion"]').inner_html()
    # pdf = PDF()
    # pdf.html_to_pdf(inner_html, "output/receipts/{}.pdf".format(receipt_no), overwrite=True)
    page.locator('#robot-preview-image').screenshot(path="output/screenshot/{}.png".format(receipt_no))
    pdf = PDF()
    list_of_files = [
        'output/receipts/{}.pdf'.format(receipt_no),
        'output/screenshot/{}.png'.format(receipt_no),
        #'robot.pdf:1',
        #'approved.png:x=0,y=0',
    ]
    pdf.add_files_to_pdf(
        files=list_of_files,
        target_document='output/receipts/{}.pdf'.format(receipt_no),
    )

def click_another_order():
    page = browser.page()
    page.click("#order-another")
    
def check_err_block():
    page = browser.page()
    try:
        errs = page.locator('//div[@role="alert"]').inner_text()
        page.click('//form/button[contains(text(),"Order")]')
        check_err_block()
    except:
        print('err')
        
def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_tar('./output/receipts', 'output/tasks.tar', recursive=True)
    