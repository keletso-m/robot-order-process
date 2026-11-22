import os
from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    """Orders robots from the Robot Spare Bin Industries website based on a CSV file.

    The task opens the ordering website, retrieves orders from a CSV file, and
    processes each order.
    """
    browser.configure(slowmo=100)
    os.makedirs("output/receipts", exist_ok=True)
    os.makedirs("output/screenshots", exist_ok=True)
    open_robot_order_website()
    orders = get_orders()
    for row in orders:
        close_annoying_modal()
        fill_the_form(row)
        preview_robot()
        submit_order()
        order_number = row["Order number"]
        pdf_file = store_receipt_as_pdf(order_number)
        screenshot = screenshot_robot(order_number)
        embed_screenshot_to_receipt(screenshot, pdf_file)
        order_another()
        archive_receipts()


def open_robot_order_website():
    """Opens the Robot Spare Bin Industries website for ordering robots.
    """
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def get_orders():
    """Retrieves the list of robot orders from a CSV file.
    """
    HTTP().download(
        url="https://robotsparebinindustries.com/orders.csv",
        overwrite=True,
    )
    return Tables().read_table_from_csv("orders.csv", header=True)


def close_annoying_modal():
    """Closes the annoying modal that appears when opening the website.
    """
    page = browser.page()
    page.click("button:text('OK')")


def fill_the_form(row):
    """Fills the robot order form with the provided data.
    """
    page = browser.page()
    page.select_option("#head", row["Head"])
    page.check(f"#id-body-{row['Body']}")
    page.fill("input[placeholder='Enter the part number for the legs']", row["Legs"])
    page.fill("#address", row["Address"])


def preview_robot():
    """Previews the robot based on the filled form.
    """
    browser.page().click("#preview")


def submit_order():
    """Submits the robot order form and handles any errors that may occur.
    """
    page = browser.page()
    page.click("#order")
    while page.is_visible(".alert-danger"):
        page.click("#order")


def store_receipt_as_pdf(order_number):
    """Stores the receipt of the robot order as a PDF file."""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf_path = f"output/receipts/receipt_{order_number}.pdf"
    PDF().html_to_pdf(receipt_html, pdf_path)
    return pdf_path


def screenshot_robot(order_number):
    """Takes a screenshot of the robot preview and saves it as a PNG file."""
    page = browser.page()
    screenshot_path = f"output/screenshots/robot_{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path


def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embeds the screenshot of the robot preview into the PDF receipt."""
    PDF().add_files_to_pdf(
        files=[screenshot],
        target_document=pdf_file,
        append=True,
    )


def order_another():
    """Clicks the 'Order Another' button to start a new order."""
    browser.page().click("#order-another")

def archive_receipts():
    """Archives all the receipts into a ZIP file."""
    Archive().archive_folder_with_zip("output/receipts", "output/receipts.zip")


